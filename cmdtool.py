#!/usr/bin/env python
#coding=utf-8

import sys  
import logging
from cmd import Cmd  

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='cli.log', level=logging.INFO, format=LOG_FORMAT)

# top cmd decorate  
def command(func):
    def wrapper(*args, **kwargs):
        logging.info('wrapper %s(%s)'%(func.__name__,args[1]))
        cmd_info = func.__name__.split('_')
        cmd_lvl = len(cmd_info) - 1
        logging.info('%s is lvl %s cmd.'% (func.__name__, cmd_lvl))
        command = cmd_info[1]
        line = args[1].strip()
        argv = line.split(' ')
        # invoke real func
        self = args[0]
        ret = func(self, argv=argv)
        return ret

    return wrapper 

class CmdTool(Cmd, object):  
      
    def __init__(self):
        Cmd.__init__(self)  
        self.identchars = self.identchars + '-'
        logging.info('stared')

    def _complete_cmd_and_opt(self, text, line, cmd_info):
        logging.info('curren postion=[%s],line:[%s]' % (text,line))
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
        text = line.split(' ')[-1]

        ret = []
        for opt in opts:
            if opt.startswith(text):
                ret.append(opt)

        logging.debug('ret=%s'%ret)
        return ret
      
    def opts_complete(self, text, line, opts):
        text = line.split(' ')[-1]

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
            arg = text[2:] if len(text)>2 else ''
            logging.debug('matching arg [%s]' % arg)
            for opt in opts:
                if opt.startswith(arg) and '--'+opt not in line:
                    ret.append(opt)

        logging.info('ret=%s'%ret)
        return ret
      
    def help_exit(self):
        print("exit program")  
      
    def do_exit(self,line):
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
        ret = [a[3:] for a in self.get_names() 
                  if a.startswith(dotext) and '_' not in a[3:] ]
        return ret

    def get_names(self):
        # This method used to pull in base class attributes
        # at a time dir() didn't do it yet.
        return dir(self.__class__)

    def _complete(self, text, state):
        """Return the next possible completion for 'text'.

        If a command has not been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
        if state == 0:
            import readline
            origline = readline.get_line_buffer()
            line = origline.lstrip()
            stripped = len(origline) - len(line)
            begidx = readline.get_begidx() - stripped
            endidx = readline.get_endidx() - stripped
            if begidx>0:
                cmd, args, foo = self.parseline(line)
                if cmd == '':
                    compfunc = self.completedefault
                else:
                    try:
                        compfunc = getattr(self, 'complete_' + cmd)
                    except AttributeError:
                        compfunc = self.completedefault
            else:
                compfunc = self.completenames

            # [patch begin] adjust current str(because readline ignore char '-')
            text = line.split(' ')[-1]
            # [patch: end]

            self.completion_matches = compfunc(text, line, begidx, endidx)
        try:
            return self.completion_matches[state]
        except IndexError:
            return None

    def complete(self, text, state):
        try:
            outlist = super(CmdTool, self).complete(text, state)  
            #outlist = self._complete(text, state)  
            if not outlist: return

            if not (outlist == '-' or outlist == '--'): 
                outlist = outlist + ' '
            return outlist
        except:
            logging.exception(sys.exc_info())


class TestCli(CmdTool):  
      
    def __init__(self):
        CmdTool.__init__(self)  
        self.prompt = '(testcmd) '
        self.intro = 'this is a cmd test program'

    @command
    def do_hello(self, argv):  
        print ('hello: %s' % argv)

    def complete_hello(self, text, line, begidx, endidx):
        opts = ['name']
        return self.opts_complete(text, line, opts)

    def help_hello(self):  
        print("hello [name]: \n\tgreeting someone")  
      
    @command
    def do_book(self, argv):  
        subcmd = 'do_book_' + argv[0]
        if hasattr(self, subcmd):
            getattr(self, subcmd)(argv[1:])
        else:
            print("Unkown sub command: book %s" % argv)  

    # @subcommand
    def do_book_list(self, argv):  
        print 'do book list :%s' % argv

    # @subcommand
    def do_book_create(self, argv):  
        print 'do book create :%s' % argv

    # @subcommand
    def do_book_delete(self, argv):  
        print 'do book delete :%s' % argv

    def complete_book(self, text, line, begidx, endidx):
        # key:subcmd, value: opts
        cmd_info= {'create': ['name', 'author'],
                   'show':['id'],
                   'delete':['id'],
                   'list':[]}
        return self._complete_cmd_and_opt(text, line, cmd_info)


if __name__ =="__main__":  
    cmd=TestCli() 
    try:
        cmd.cmdloop()
    except KeyboardInterrupt:
        print 'bye'
