import jp_proxy_widget
import IPython, time

import os
script_path = os.path.dirname(os.path.abspath( __file__ ))
    
class MLJobMonitor:
    def __init__(self):
        self._W=jp_proxy_widget.JSProxyWidget()
        self._initialize_widget(self._W)
    def display(self):
        display(self._W)
    def widget(self):
        return self._W.element
    def renderNow(self):
        # See https://github.com/AaronWatters/jp_proxy_widget/issues/2
        time.sleep(0.1) # It is unclear how long one needs to sleep... e.g., 0.001 does not seem to work
        IPython.get_ipython().kernel.do_one_iteration()
    def _initialize_widget(self,W):
        W.check_jquery()
        
        with open(script_path+'/mljobmonitor.js') as f:
            script=f.read()
            W.js_init(script)
        
        W.js_init("""
            window.MLJobMonitor(element);
        """);