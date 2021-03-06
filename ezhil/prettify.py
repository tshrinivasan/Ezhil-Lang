#!/usr/bin/python
## -*- coding: utf-8 -*-
## 
## (C) 2008, 2013 Muthiah Annamalai
## Licensed under GPL Version 3
## 
## This module is the pretty-printer for the Ezhil language.
## It contains classes @WikiStyle, @Printer
## 

from theme import XsyTheme
from ezhil_scanner import EzhilLex, EzhilToken
from ezhil import EzhilInterpreter
from transform import Visitor

class WikiStyle:
    @staticmethod
    def wrap_msg(attrib,text):
        """ @text is any character stream that has to be wrapper in a style-Theme,
            specified by @attrib """
        if ( len(attrib) >= 1 ):
            out = '<span style="color:#'+attrib[0]
        if ( len(attrib) >= 2 ):
            out = out + ';background:#'+attrib[1]
        out = out + '">' + attrib.process(text) + "</span>"
        return out

class Printer(Visitor):
    def __init__(self,src_file):
        """ @styler uses a Wiki/HTML/LaTeX output formatter, with a color theme 
        specificied by @theme to render the text into the appropriate format"""
        Visitor.__init__(self)
        self.styler = WikiStyle.wrap_msg
        self.theme = XsyTheme()
        self.lexer = EzhilLex(src_file)
        #print self.lexer.comments.keys()
        self.output = []
        self.line = 1 #current line 
        self.NEWLINE = "<BR />\n"
        
    def update_line(self,obj):
        #print obj.line,"= line"
        if ( obj.line > self.line ):
            self.line = obj.line
            self.append( self.NEWLINE  )
        if ( self.lexer.comments.has_key(self.line) ):
            #print "visiting comment "
            self.append( self.lexer.comments[self.line] )
            del self.lexer.comments[self.line]
        return
    
    def append(self,string):
        self.output.append( string )
    
    def default(self,*args):
        """ /dev/zero dump for all visitor methods when not handled in derived class"""
        #args[0] is AST object
        self.append( "def :")
        self.update_line(args[0])
        self.append(str(args[0]))
        
    def visit_identifier(self, IDobj):  
        attrib = self.theme.Variables
        self.update_line(IDobj)
        self.append( self.styler(attrib,str(IDobj.id)))
        return
    
    def visit_string(self, string):
        attrib = self.theme.LiteralString
        self.update_line(string)
        self.append(self.styler(attrib,str(string)))
        return

    def visit_number(self, num):
        attrib = self.theme.LiteralNumber
        self.update_line(num)
        self.append(self.styler(attrib,str(num)))
        return

    def visit_expr_call(self,expr_call):
        var_attrib = self.theme.Variables
        self.update_line(expr_call)
        self.append(self.styler(var_attrib,str(expr_call.func_id.id)))
        op_attrib = self.theme.Operators
        self.append( self.styler(op_attrib,"(") )
        expr_call.arglist.visit( self )
        self.append( self.styler(op_attrib,")") )
        return

    def visit_expr_list(self, expr_list):
        for pos,exp_itr in enumerate(expr_list.exprs):
            self.update_line(exp_itr)
            exp_itr.visit( self )
            if (pos+1) < len(expr_list.exprs):
                self.append(",")
            
        return
    
    def visit_stmt_list(self,stmt_list):
        for stmt in stmt_list.List:
            stmt.visit(self)
            self.update_line(stmt)
            self.append(self.NEWLINE)
        return
    
    def visit_stmt( self, stmt):
        ## is this a recipe for getting stuck in a loop?
        self.update_line(stmt)
        stmt.visit(self)
        return
    
    def visit_expr(self, expr):
        op_attrib = self.theme.Operators
        self.update_line(expr)
        expr.term.visit(self)
        self.append( self.styler(op_attrib, EzhilToken.token_types[expr.binop.kind] ) )
        expr.next_expr.visit(self)
        return
    
    def visit_return_stmt(self, ret_stmt):
        kw_attrib = self.theme.Keywords
        self.update_line(ret_stmt)        
        keyword = "பின்கொடு"
        self.append( self.styler( kw_attrib, keyword ) )
        self.append( self.NEWLINE )
        return
    
    def visit_break_stmt(self, break_stmt ):
        kw_attrib = self.theme.Keywords
        self.update_line(ret_stmt)
        keyword = "நிறுத்து" #EzhilToken.Keywords["break"]
        self.append( self.styler( kw_attrib, keyword ) )
        self.append( self.NEWLINE )
        return
    
    def visit_continue_stmt(self, cont_stmt):
        kw_attrib = self.theme.Keywords
        self.update_line(ret_stmt)
        keyword = "தொடர்" #EzhilToken.Keywords["continue"]
        self.append( self.styler( kw_attrib, keyword ) )
        self.append( self.NEWLINE )        
        return
    
    def visit_else_stmt(self,else_stmt):
        kw_attrib = self.theme.Keywords
        keyword = "இல்லை"
        self.append( self.styler( kw_attrib, keyword ) )
        self.update_line(else_stmt)
        else_stmt.stmt.visit( self )
        return
    
    def visit_if_elseif_stmt(self,if_elseif_stmt):
        op_attrib = self.theme.Operators
        
        # condition expression
        self.append( self.styler( op_attrib, "@( " ) )
        if_elseif_stmt.expr.visit(self)
        self.append( self.styler( op_attrib, ") " ) )
        
        # IF kw
        kw_attrib = self.theme.Keywords
        keyword_if = "ஆனால்"
        self.append( self.styler( kw_attrib, keyword_if ) )                
        
        # True-Body
        if_elseif_stmt.body.visit( self )
        
        # False-Body - optionally present
        if hasattr(if_elseif_stmt.next_stmt,'visit'):
            if_elseif_stmt.next_stmt.visit(self)
        
        self.visit_end_kw()
        
    def visit_end_kw(self):
        # END kw
        kw_attrib = self.theme.Keywords
        keyword_end = "முடி"
        self.append( self.styler( kw_attrib, keyword_end ) )
        
    def visit_while_stmt(self,stmt):
        self.default(stmt)
        return

    def visit_for_stmt(self,for_stmt):
        self.default(for_stmt)
        return

    def visit_assign_stmt(self, assign_stmt):
        op_attrib = self.theme.Operators
        assign_stmt.lvalue.visit( self )
        self.append(self.styler(op_attrib,"="))        
        assign_stmt.rvalue.visit( self )
        return

    def visit_print_stmt(self, print_stmt):
        kw_attrib = self.theme.Keywords
        keyword = "பதிப்பி"
        self.update_line(print_stmt)
        self.append( self.styler(kw_attrib,str(keyword)) )
        print_stmt.exprlst.visit(self)
        return

    def visit_eval_stmt(self, eval_stmt ):
        eval_stmt.expr.visit(self)
        return
    
    def visit_arg_list(self, arg_list):
        self.default(arg_list)
        return

    def visit_value_list(self,value_list):
        op_attrib = self.theme.Operators
        for value in value_list.args:
            self.update_line(value)
            value.visit(self)
            self.append(self.styler(op_attrib,","))
        self.output.pop()
        return

    def visit_function(self,function):
        self.default(function)
        return
    
    def pretty_print(self):
        self.parse_eval = EzhilInterpreter(self.lexer)
        ast = self.parse_eval.parse()
        print ast
        ast.visit(self)

        # dump remaining comments
        comm_attrib = self.theme.Comment
        for  line,comment in  self.lexer.comments.items():            
            self.append( self.styler( comm_attrib, comment ) )
            self.append( self.NEWLINE )
        
        print "".join(self.output)
    
    # method walks the lexer-tokens and calls the appropriate elements
    # basic lexical hiliting
    def lexical_hilite(self):
        self.lexer.tokens.reverse()
        out = []
        for t in self.lexer.tokens:
            add_br = False
            attrib = self.theme.Operators
            if EzhilToken.is_keyword(t.kind):
                attrib = self.theme.Keywords
                if ( EzhilToken.get_name(t.kind) in ["END", "ELSE"] ):
                    out.append('<BR />\n')
            elif EzhilToken.is_number(t.kind):
                attrib = self.theme.LiteralNumber
            elif EzhilToken.is_string(t.kind):
                attrib = self.theme.LiteralString
                t.val = '"'+t.val+'"' #FIXME: ideally do some escaping as well
            elif EzhilToken.is_id(t.kind):
                attrib = self.theme.Variables
            elif( t.val in ["@", "பதிப்பி" ] ):
                attrib = self.theme.Builtins
                out.append('<BR />\n')
            
            t.val = " " + str(t.val)
            out.append( self.styler(attrib,t.val) )
            if ( add_br ):
                out.append("<BR />\n")
        
        return "".join(out)

if __name__ == "__main__":
    from sys import argv,exit
    if len(argv) <= 1:
        print "usage: python ezhil/prettify.py <file1> <file2> ... "
        exit(-1)
    for aFile in argv[1:]:
        print "working with ",aFile
        Printer(aFile).pretty_print()
    
