#!/usr/bin/env python
#coding=utf-8

import sys  
import logging
from cmd import Cmd  

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='cli.log', level=logging.INFO, format=LOG_FORMAT)
  
class CmdTest(Cmd, object):  
      
    def __init__(self):            #初始基础类方法  
        Cmd.__init__(self)  
        self.identchars = self.identchars + '-'
        self.prompt = '(natgateway) '
        self.intro = 'natgateway cli'
        logging.info('stared')
          
    def help_snat(self):  
        print("snat operations")  
      
    def do_natgateway(self,line):  
        command = 'natgateway'
        line = line.strip()
        argv = [command]+line.split(' ')
        print("argv: %s" % argv)  

    def do_dnat(self,line):  
        command = 'dnat'
        line = line.strip()
        argv = [command]+line.split(' ')
        print("argv: %s" % argv)  

    def do_snat(self,line):  
        command = 'snat'
        line = line.strip()
        argv = [command]+line.split(' ')
        print("argv: %s" % argv)  

    def complete_natgateway(self, text, line, begidx, endidx):
        cmd_info= {'create': ['vpc_id', 'subnet_id'],
                   'show':['id'],
                   'delete':['id'],
                   'list':[]}
        return self._complete_cmd_and_opt(text, line, cmd_info)

    def complete_snat(self, text, line, begidx, endidx):
        cmd_info= {'create': ['cidr', 'eip'],
                   'show':['id'],
                   'delete':['id'],
                   'list':['nat_gateway_id']}
        return self._complete_cmd_and_opt(text, line, cmd_info)

    def complete_dnat(self, text, line, begidx, endidx):
        cmd_info= {'create':
                     ['proto', 'ext_ip', 'ext_port','int_ip', 'int_port'],
                   'show':['id'],
                   'delete':['id'],
                   'list':['nat_gateway_id']}
        return self._complete_cmd_and_opt(text, line, cmd_info)

    def _complete_cmd_and_opt(self, text, line, cmd_info):
        logging.info('curren postion=[%s],line:[%s]' % (text,line))
        text = line.split(' ')[-1]
        # dnat crea...
        argv = line.split(' ')
        logging.info('argv: %s'%argv)
        if len(argv) == 2:
            actions = cmd_info.keys()
            return self.action_complete(text, line, actions)
        # dnat create --proto tcp --port
        if len(argv) > 2:
            action = argv[1]
            last_arg = argv[-2]
            logging.info('action: %s, last arg:%s' % (action,last_arg))
            if last_arg.startswith('--'):
                # todo: enum opt value, such as proto=[tcp/udp]
                return []
            opts = cmd_info[action]
            return self.opts_complete(text, line, opts)

    def action_complete(self, text, line, opts):
        ret = []
        for opt in opts:
            if opt.startswith(text):
                ret.append(opt)

        logging.debug('ret=%s'%ret)
        return ret
      
    def opts_complete(self, text, line, opts):
        logging.info('matching opt [%s], from %s' % (text, opts))
        argv = line.split(' ')
        ret = []
        need_more_opts = False
        for opt in opts:
            if '--'+opt not in line:
                need_more_opts = True
                break
        if not need_more_opts:
            return []
        if not text:
            return ['--']
        if text == '-':
            return ['-']

        if text.startswith('--'):
            arg = text[2:]
            logging.debug('matching arg [%s]' % arg)
            for opt in opts:
                if opt.startswith(arg) and '--'+opt not in line:
                    ret.append(opt)

        logging.info('ret=%s'%ret)
        return ret
      
    def help_exit(self):          #以help_*开头的为帮助  
        print("输入exit退出程序")  
      
    def do_exit(self,line):       #以do_*开头为命令  
        print("Exit:",line)  
        sys.exit()  

    def parseline(self, line):
        """Parse the line into a command name and a string containing
        the arguments.  Returns a tuple containing (command, args, line).
        'command' and 'args' may be None if the line couldn't be parsed.
        """
        line = line.strip()
        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
        elif line[0] == '!':
            if hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            else:
                return None, None, line
        i, n = 0, len(line)
        while i < n and line[i] in self.identchars:
            i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

    def completenames(self, text, *ignored):
        dotext = 'do_'+text
        ret = [a[3:] for a in self.get_names() if a.startswith(dotext)]
        return ret

    def get_names(self):
        # This method used to pull in base class attributes
        # at a time dir() didn't do it yet.
        return dir(self.__class__)

    def complete(self, text, state):
        try:
            outlist = super(CmdTest, self).complete(text, state)  
            if not outlist: return

            if not (outlist == '-' or outlist == '--'): 
                outlist = outlist + ' '
            return outlist
        except:
            logging.exception(sys.exc_info())


if __name__ =="__main__":  
    cmd=CmdTest() 
    try:
        cmd.cmdloop()
    except:
        logging.info('exited.')
        print 'bye'
