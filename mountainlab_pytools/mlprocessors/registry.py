#!/usr/bin/env python

import json

import os
import traceback

class ProcessorRegistry:
    def __init__(self, processors = []):
      self.processors = processors

    def spec(self):
      s = {}
      s['processors'] = [ cls.spec() for cls in self.processors ]
      return s

    def find(self, **kwargs):
        for P in self.processors:
            for key in kwargs:
                if not hasattr(P, key):
                    #print(key, "not in P")
                    continue
                if getattr(P, key) != kwargs[key]:
                    #print(getattr(P, key), "doesn't match", kwargs[key])
                    continue
                return P

    def get_processor_by_name(self, name):
        return self.find(NAME = name)

    def test(self, args, **kwargs):
        procname = args[0]
        proc = self.find(NAME = procname)
        if not proc:
            raise KeyError("Unable to find processor %s" % procname)
        if not hasattr(proc, 'test') or not callable(proc.test):
            raise AttributeError("No test function defined for %s" % proc.NAME)
        print("----------------------------------------------")
        print("Testing", proc.NAME)
        try:
            result = proc.test()
            print("SUCCESS" if result else "FAILURE")
        except Exception as e:
            print("FAILURE:", e)
            if kwargs.get('trace', False): traceback.print_exc()
        finally:
            print("----------------------------------------------")

    def process(self, args):
      opcode = args[1]
      if opcode == 'spec':
          print(json.dumps(self.spec(), sort_keys = True, indent=4))
          return
      if opcode == 'test':
          try:
            self.test(args[2:], trace=os.getenv('TRACEBACK', False) not in [ '0', 0, 'False', 'F', False ])
          except KeyError as e:
            # taking __str__ from Base to prevent adding quotes to KeyError
            print(BaseException.__str__(e))
          except Exception as e:
            print(e)
          finally:
            return
      if opcode in [ x.NAME for x in self.processors ]:
          self.invoke(self.get_processor_by_name(opcode), args[2:])
      else:
        print("Processor {} not found".format(opcode))

    def invoke(self, proc, args):
        proc.invoke(args)

def register_processor(registry):
    def decor(cls):
      registry.processors.append(cls)
      return cls
    return decor


registry = ProcessorRegistry()
