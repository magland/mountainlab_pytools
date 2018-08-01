from . import validators
from .validators import FileExistsValidator, ValidationError

from functools import lru_cache
import argparse
import sys
import traceback

class Input():
    def __init__(self, description = None, optional = False, multi = False, validators = None, *args, **kwargs):
        self.description = description
        self.optional = optional
        self.multi = multi
        self.validators = validators or []
        self.validators.append(FileExistsValidator())
        # self.formats = []

    def prepare(self, arg):
        pass

    @property
    def spec(self):
      return { 'name': self.name, 'description': self.description, 'optional': self.optional }


class Output():
    def __init__(self, description = None, optional = False, multi = False, validators = None, *args, **kwargs):
        self.description = description
        self.optional = optional
        self.multi = multi
        self.validators = validators or []

    def prepare(self, arg):
        pass

    @property
    def spec(self):
      return { 'name': self.name, 'description': self.description, 'optional': self.optional }


class StreamInput(Input):
    """
      Processor input that preps the file for reading
    """

    mode = 'rb'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'mode' in kwargs: self.mode = kwargs['mode']

    def prepare(self, arg):
        return open(arg, self.mode)

class StreamOutput(Output):
    """
        Processor output that preps the file for writing
    """
    mode = 'wb'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'mode' in kwargs: self.mode = kwargs['mode']

    def prepare(self, arg):
        return open(arg, self.mode)

class Parameter():
    def __init__(self, **kwargs):
        self.default = kwargs.get('default', None)
        self.description = kwargs.get('description', '')
        self.optional = kwargs.get('optional', False)
        self.multi = kwargs.get('multi', False)
        self.choices = kwargs['choices'] if 'choices' in kwargs else []
        self.validators = kwargs.get('validators', [])

    def __repr__(self):
        if hasattr(self, 'name'): return self.name
        return super().__repr__()

    def clean(self, value):
        try:
            return self.datatype(value)
        except:
            return value

    @property
    def spec(self):
      if isinstance(self.datatype, tuple):
          dt = "{major}<{minor}>".format(major = self.datatype[0].__name__, minor = self.datatype[1].__name__)
      else:
        dt = self.datatype.__name__
      if dt == 'str': dt = 'string'
      s = { 'name': self.name, 'description': self.description, 'datatype': dt, 'optional': self.optional }
      if self.optional or self.default:
          s['default_value'] = str(self.default)
      return s

class BoolParameter(Parameter):
    def __init__(self, description = '', **kwargs):
        if not 'description' in kwargs:
            kwargs['description'] = description
        super().__init__(**kwargs)
        self.datatype = bool
        if not 'choices' in kwargs: self.choices = [ True, False ]

    def clean(self, value):
        if value == 'True' or value == 'true' or value == '1': return True
        return False

class StringParameter(Parameter):
    def __init__(self, description = '', **kwargs):
        if not 'description' in kwargs:
            kwargs['description'] = description
        super().__init__(**kwargs)
        self.datatype = str
        if 'regex' in kwargs:
          self.validators.append(validators.RegexValidator(kwargs['regex']))

class ArithmeticParameter(Parameter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'min' in kwargs or 'max' in kwargs:
            self.validators.append(validators.ValueValidator(**kwargs))

class IntegerParameter(ArithmeticParameter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.datatype = int

class FloatParameter(ArithmeticParameter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.datatype = float

class IntegerListParameter(StringParameter):
    def __init__(self, description='', **kwargs):
        super().__init__(description, **kwargs)
        self.datatype = (list, int)

        def validate(value):
            vals = value.split(',')
            try:
                intvals = [ int(x) for x in vals ]
            except:
                raise ValidationError("Input data incorrect")
        self.validators.append(validate)
    def clean(self, value):
        vals = value.split(',')
        if not vals: return []
        return [ int(x) for x in vals ]

class ProcMeta(type):
    """
        The metaclass is responsible for processing a class definition.

        Current features:
            - cls.NAME is assembled from class name and contents of NAMESPACE (TODO: consider package/module name)
            - cls.VERSION is set to 0.0.1 if not defined explicitly
            - cls.DESCRIPTION is taken from docstring if not defined explicitly
            - cls.INPUTS is assembled from class definition
            - cls.OUTPUTS is assembled from class members definition
            - cls.PARAMETERS is assembled from class members definition


    """
    def __new__(cls, name, bases, attrs, **kwargs):
      super_new = super().__new__

      parents = [b for b in bases if isinstance(b, ProcMeta)]
      # don't process Processor
      if not parents:
          return super_new(cls, name, bases, attrs)

      # todo: remove detected ins,outs,params from attrs
      new_class = super_new(cls, name, bases, attrs, **kwargs)
      name_components = []
      if 'NAMESPACE' in attrs and attrs['NAMESPACE']: name_components.append(attrs['NAMESPACE'])
      if 'NAME' in attrs and attrs['NAME']:
        name_components.append(attr['NAME'])
      else:
        name_components.append(name)
      new_class.NAME = '.'.join(name_components)
      if not 'VERSION' in attrs:
        new_class.VERSION = '0.0.1'
      if not 'DESCRIPTION' in attrs:
        if '__doc__' in attrs:
          doc = attrs['__doc__']
          # find first empty line
          empty_line = doc.find('\n\n')
          if empty_line >= 0: doc = doc[:empty_line]
          doc = ' '.join([ x.strip() for x in doc.strip().splitlines()])

          new_class.DESCRIPTION = doc
        else:
          new_class.DESCRIPTION = '{} MountainLab processor'.format(new_class.NAME)

      new_class.__doc__ = new_class.DESCRIPTION
      # inherit from parent
      if not hasattr(new_class, 'INPUTS'):
        new_class.INPUTS = []
      else: new_class.INPUTS = new_class.INPUTS.copy()
      if not hasattr(new_class, 'OUTPUTS'):
        new_class.OUTPUTS = []
      else: new_class.OUTPUTS = new_class.OUTPUTS.copy()
      if not hasattr(new_class, 'PARAMETERS'):
        new_class.PARAMETERS = []
      else: new_class.PARAMETERS = new_class.PARAMETERS.copy()

      for attr in attrs:
        if isinstance(attrs[attr],  Input):
          attrs[attr].name = attr
          new_class.INPUTS.append(attrs[attr])
        if isinstance(attrs[attr], Output):
          attrs[attr].name = attr
          new_class.OUTPUTS.append(attrs[attr])
        if isinstance(attrs[attr], Parameter):
          attrs[attr].name = attr
          if attrs[attr].default is not None and not attrs[attr].optional:
              raise Exception("{}: Can't have a non-optional parameter with a default value".format(attr))
          new_class.PARAMETERS.append(attrs[attr])

      return new_class


class Processor(metaclass=ProcMeta):
    NAMESPACE=None
    VERSION = None
    DESCRIPTION = None
    COMMAND = None
    USE_ARGUMENTS = True

    @classmethod
    def _init(cls, self, *args, **kwargs):
        for key in kwargs:
          #print(key)
          if key in [ x.name for x in cls.INPUTS ]:
            setattr(self, key, kwargs[key])
          if key in [ x.name for x in cls.OUTPUTS ]:
            setattr(self, key, kwargs[key])
          if key in [ x.name for x in cls.PARAMETERS ]:
            setattr(self, key, kwargs[key])


    def __init__(self, *args, **kwargs):
        self._init(self, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.run(*args, **kwargs)

    @classmethod
    @lru_cache()
    def spec(self):
        """
            Generates spec for the processor as a Python dictionary.
        """
        pspec = {}
        pspec['name'] = self.NAME
        pspec['version'] = self.VERSION
        pspec['description'] = self.DESCRIPTION
        #if hasattr(self, 'run') and callable(self.run):
        components = [sys.argv[0], self.NAME]
        if self.USE_ARGUMENTS: components.append('$(arguments)')
        pspec['exe_command'] = self.COMMAND or ' '.join(components)

        pspec['inputs'] = [ inp.spec for inp in self.INPUTS ]
        pspec['outputs'] = [ out.spec for out in self.OUTPUTS ]
        pspec['parameters'] = [ param.spec for param in self.PARAMETERS ]
        if hasattr(self, 'test') and callable(self.test):
            pspec['has_test'] = True

        return pspec

    @classmethod
    def invoke_parser(self, supparser=None):
        """
            Creates a commandline parser for the processo
        """
        if supparser:
            parser = supparser.add_parser(self.NAME, description=self.DESCRIPTION)
        else:
            parser = argparse.ArgumentParser(prog=self.NAME, description=self.DESCRIPTION)
        # populate parser with INPUTS
        for input in self.INPUTS:
            opts = {}
            opts['help'] = input.description
            opts['required'] = not input.optional
            if input.multi: opts['action'] = 'append'
            parser.add_argument('--'+input.name, **opts)

        # populate parser with OUTPUTS
        for output in self.OUTPUTS:
            opts = {}
            opts['help'] = output.description
            opts['required'] = not output.optional
            if output.multi: opts['action'] = 'append'
            parser.add_argument('--'+output.name, **opts)

        # populate parser with PARAMETERS
        for param in self.PARAMETERS:
            opts = {}
            opts['help'] = param.description
            opts['required'] = not param.optional
            if isinstance(param.datatype, tuple):
                opts['type'] = str
                #opts['type'] = param.datatype[1]
            else:
                opts['type'] = param.datatype

            if param.multi: opts['action'] = 'append'
            if param.choices:
                if isinstance(param.choices, tuple):
                    # if choices is a tuple, assume it is a tuple of mappings
                    # and expand them
                    opts['choices'] = [ choice[0] for choice in param.choices ]
                else:
                    opts['choices'] = param.choices
            parser.add_argument('--'+param.name, **opts)

        if self.USE_ARGUMENTS:
            parser.add_argument('--_tempdir',required=False, help=argparse.SUPPRESS)
        return parser

    @classmethod
    def invoke(proc, args):
        """
            Executes the processor passing given arguments
        """
        parser = proc.invoke_parser()
        opts = parser.parse_args(args)
        kwargs = {}
        try:
            for input in proc.INPUTS:
                inputname = input.name
                if hasattr(opts, inputname) and getattr(opts, inputname) is not None:
                    # for multi=True inputs, handle each input separately
                    if isinstance(getattr(opts, inputname), list):
                        inputlist = getattr(opts, inputname)
                    else:
                        inputlist = [ getattr(opts, inputname)]
                    for inputelem in inputlist:
                        # TODO: validate all fields instead of bailing out after first exception
                        for validator in input.validators:
                            validator(inputelem)
                    if hasattr(opts, input.name):
                        prepared = input.prepare(getattr(opts, input.name)) or getattr(opts, input.name)
                        kwargs[input.name] = prepared
            for output in proc.OUTPUTS:
                outputname = output.name
                if hasattr(opts, outputname) and getattr(opts, outputname) is not None:
                    # for multi=True outputs, handle each input separately
                    if isinstance(getattr(opts, outputname), list):
                        outputlist = getattr(opts, outputname)
                    else:
                        outputlist = [ getattr(opts, outputname)]
                    for outputelem in outputlist:
                        # TODO: validate all fields instead of bailing out after first exception
                        for validator in output.validators:
                            validator(outputelem)
                    if hasattr(opts, output.name):
                        prepared = output.prepare(getattr(opts, output.name)) or getattr(opts, output.name)
                        kwargs[output.name] = prepared
                elif output.optional:
                    kwargs[output.name] = None
                else:
                    raise AttributeError('Missing value for {} output'.format(outputname))
            for param in proc.PARAMETERS:
                if hasattr(opts, param.name) and getattr(opts, param.name) is not None:
                    value = getattr(opts, param.name)
                    # validate if needed
                    for validator in param.validators:
                        validator(value)
                    # if param is a tuple of choices, each choice is a tuple itself
                    # with first element of the input value and second element
                    # containing the value to be passed to the processor
                    if param.choices and isinstance(param.choices, tuple):
                        for choice in param.choices:
                            if choice[0] == value:
                                kwargs[param.name] = choice[1]
                                break
                    else:
                        kwargs[param.name] = value
                elif param.optional:
                    kwargs[param.name] = param.default
                else:
                    raise AttributeError('Missing value for {} parameter'.format(param.name))
            inst = proc(**kwargs)
            inst.run()
            # todo: cleanup
        except Exception as e:
            print("Error:", e)
            #traceback.print_exc()
