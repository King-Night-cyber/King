import sys
from sys import *
import os,platform
from colorama import init
from termcolor import colored
from itertools import cycle, islice, dropwhile

#defining some variables for later use
DIGITS = "1234567890"
SIGNS = "+-*/"
SPECIAL_SIGNS = "<>"

version = "0.1.0"

#dictionary for the variables
table = {}

match = False

#run: main function
def run():
	try:
		if argv[1].endswith(".king"):
			data = readf(argv[1])
			tokens = lex(data)
			parse(tokens)
		else:
			error("File Error: Given file is not a King file!")
	except IOError:
		error("File Error: No file given!")

#readf: reads file content and appends end-of-file tag
def readf(file):
	data = open(file, "r").read()
	data += "<EOF>"
	return data

#initialise colorama
init()
#error: prints an error message with red background
def error(text):
	print(colored(text, "white", "on_red"))

#message: prints an colored message
def message(text, color, background_color = None):
	print(colored(text, color, background_color))

#lex: scan the data he gets and tag it accordingly
def lex(data):
	data = list(data)

	state = 0
	hasSing = False
	varStart = False

	token = ""
	string= ""
	expression = ""
	var = ""
	comment = ""
	
	tokens = []

	for char in data:
		token += char

		#if the token is a new line or the ond-of-file tag...
		if token == "\n" or token == "<EOF>":
			#if hasSign is True, append an expression...
			if expression != "" and hasSing == True:
				tokens.append("expression " + expression)
				expression = ""
				hasSing = False
				token = ""

			#...else append a number
			elif expression != "" and hasSing == False:
				tokens.append("number " + expression)
				expression = ""
				hasSing = False
				token = ""

			#when it's done, append it
			elif var != "":
				var = var.replace("var", "")
				tokens.append("var " + var)
				var = ""
				varStart = False
				token = ""

			#otherwise clear the token
			token = ""

		#ignore tabs
		if token == "\t":
			tokens.append("tab")
			token = ""

		#if the token is an empty space, remove it...
		if token == " ":
			#...but remove it only if it's not in a string
			if state != 1:
				token = ""

		#if the token is the function "print", append it for later use
		elif token == "print":
			tokens.append("print")
			token = ""

		#if the token is a string, save it for later use
		elif token == "\"" or token  == " \"":
			if state == 0:
				state += 1
			elif state == 1:
				tokens.append("string " + string)
				string = ""
				state = 0
				token = ""
		elif state == 1:
			string += token
			token = ""

		elif token == "!":
			if expression != "" and hasSing == False:
				tokens.append("number " + expression)
				expression = ""
			tokens.append("not")
			token = ""

		#if the token is an equal sign and it's not in a string, append it in tokens
		elif token == "=" and state == 0:
			#break out if before/after a number
			if expression != "" and hasSing == False:
				tokens.append("number " + expression)
				expression = ""
			#break out if before/after an expression
			if expression != "" and hasSing == True:
				tokens.append("expression " + expression)
				expression = ""
			#break out if before/after a variable
			if var != "":
				var = var.replace("var", "")
				tokens.append("var " + var)
				var = ""
				varStart = False
			if tokens[-1] == "equal":
				tokens[-1] = "double_equal"
			elif tokens[-1] == "not":
				tokens[-1] = "not_equal"
			else:
				tokens.append("equal")
			token = ""

		#if the token is a variable declareation and it's not in a string, start append the tokens
		elif token == "var" and state == 0:
			varStart = True
			var += token
			token = ""

		#if the variable has started...
		elif varStart == True:
			#...and it's not in the SPECIAL_SIGNS list...
			if token in SPECIAL_SIGNS:
				if var != "":
					#...remove the var string...
					var = var.replace("var", "")
					#...and append it to tokens
					tokens.append("var " + var)
					var = ""
					varStart = False
			var += token
			token = ""

		#if the token is the "run" command, append it for later use
		elif token == "run":
			tokens.append("run")
			token = ""

		#if the token is the "import" command, append it for later use 
		elif token == "import":
			tokens.append("import")
			token = ""

		#if the token is the "pop" command, append it for later use
		elif token == "pop":
			tokens.append("pop")
			token = ""

		#if the token is the "input" command, append it for later use
		elif token == "input":
			tokens.append("input")
			token = ""

		#if the token is a complete if statement, append everything needed and save it for later use
		elif token == "endif":
			tokens.append("endif")
			token = ""

		elif token == "if":
			tokens.append("if")
			token = ""

		elif token == "then":
			if expression != "" and hasSing == False:
				tokens.append("number " + expression)
				expression = ""
			if expression != "" and hasSing == True:
				tokens.append("expression " + expression)
				expression = ""
			if var != "":
				var = var.replace("var", "")
				tokens.append("var " + var)
				varStart = False
				var = ""
			tokens.append("then")
			token = ""

		#if the token is in the DIGITS variable, add it to the expression string
		elif token in DIGITS:
			expression += token
			token = ""
		#if the token is in the SIGNS variable, it means that it's an expression and not a number
		elif token in SIGNS:
			hasSing = True
			expression += token
			token = ""

	#return all the tokens, so the parse can parse them
	print(tokens)
	return tokens

#frun: this is the "run" function, made exclusively for the command "run"
def frun(file):
	#check if the file exists...
	try:
		data = readf(file)
		tokens = lex(data)
		parse(tokens)
	#...else print an error message
	except IOError:
		error("File Error: Given file is non-existent!")
		exit()

#assign: assigns to the dictionary a variable name and value
def assign(name, value):
	table[name[4:]] = value

#value: retrieves the value of a specific variable
def value(name):
	if name in table:
		return table[name]
	else:
		error("Variable Error: Given variable \"" + name + "\" is not declared nor defined!")
		return("VarError")

#getInput: gets an input from the user
def getInput(text, var):
	#get the input
	i = input(text + " ")

	#...and assign it
	table[var] =  i

#parse: this is the parse, wich will decode the function we will put in
def parse(tokens):
	i = 0
	while(i < len(tokens)):
		#PRINT FUNCTION
		if tokens[i] == "print":
			if tokens[i] + " " + tokens[i+1][0:8] == "print string \"" or tokens[i] + " " + tokens[i+1][0:7] == "print number " or tokens[i] + " " + tokens[i+1][0:11] == "print expression " or tokens[i] + " " + tokens[i+1][0:4] == "print var ":
				if tokens[i+1][0:8] == "string \"": #is it a string?
					print(tokens[i+1][8:])
				elif tokens[i+1][0:7] == "number ": #is it a number?
					print(tokens[i+1][7:])
				elif tokens[i+1][0:11] == "expression ": #is it an expression?
					print(eval(tokens[i+1][11:]))
				elif tokens[i+1][0:4] == "var ": #is it an expression?
					print(value(tokens[i+1][4:]))
				i += 2

		#RUN FUNCTION
		elif tokens[i] == "run":
			if tokens[i] + " " + tokens[i+1][0:8] == "run string \"":
				if tokens[i+1][0:8] == "string \"": #is it a string?
					frun(tokens[i+1][8:])
				i += 2

		#VARIABLE DECLARATION
		elif tokens[i][0:3] == "var":
			if tokens[i][0:3] + " " + tokens[i+1] + " " + tokens[i+2][0:8] == "var equal string \"" or tokens[i][0:3] + " " + tokens[i+1] + " " + tokens[i+2][0:7] == "var equal number " or tokens[i][0:3] + " " + tokens[i+1] + " " + tokens[i+2][0:11] == "var equal expression " or tokens[i][0:3] + " " + tokens[i+1] + " " + tokens[i+2][0:4] == "var equal var ":
				if tokens[i+2][0:8] == "string \"": #is it a string?
					assign(tokens[i], tokens[i+2][8:])
				elif tokens[i+2][0:7] == "number ": #is it a number?
					assign(tokens[i], tokens[i+2][7:])
				elif tokens[i+2][0:11] == "expression ": #is it an expression?
					assign(tokens[i], str(eval(tokens[i+2][11:])))
				elif tokens[i+2][0:4] == "var ": #is it another variable?
					assign(tokens[i], str(value(tokens[i+2][4:])))
				i += 3
		

	
		#POP FUNCTION
		elif tokens[i] == "pop":
			if tokens[i] + " " + tokens[i+1][0:4] == "pop var ":
				if tokens[i+1][4:] in table:
					table.pop(tokens[i+1][4:])
					message("System: Removed variable " + tokens[i+1][4:], "yellow")
				else:
					error("Variable Error: Given variable \"" + tokens[i+1][4:] + "\" is not declared nor defined!")
				i += 2


		#INPUT FUNCTION
		elif tokens[i] == "input":
			if tokens[i] + " " + tokens[i+1][0:8] + " " + tokens[i+2][0:4] == "input string \" var ":
				getInput(tokens[i+1][8:], tokens[i+2][4:])
				i += 3

		#IF STATEMENT
		#endif
		elif tokens[i] == "endif":
			print("end of if")
			i += 1

		#if
		elif tokens[i] == "if":
			if tokens[i] + " " + tokens[i+1][0:6] + " " + tokens[i+2] + " " + tokens[i+3][0:6] + " " + tokens[i+4] == "if number double_equal number then" or tokens[i] + " " + tokens[i+1][0:8] + " " + tokens[i+2] + " " + tokens[i+3][0:8] + " " + tokens[i+4] == "if string \" double_equal string \" then" or tokens[i] + " " + tokens[i+1][0:10] + " " + tokens[i+2] + " " + tokens[i+3][0:10] + " " + tokens[i+4] == "if expression double_equal expression then":# or tokens[i] + " " + tokens[i+1][0:3] + " " + tokens[i+2] + " " + tokens[i+3][0:3] + " " + tokens[i+4] == "if var double_equal var then":
					if tokens[i+1][0:7] and tokens[i+3][0:7] == "number ": #are those numbers?
						if tokens[i+1][7:] ==  tokens[i+3][7:]: #do them match?
							match = True
					if tokens[i+1][0:8] and tokens[i+3][0:8] == "string \"": #are those strings?
						if tokens[i+1][8:] ==  tokens[i+3][8:]: #do them match?
							match = True
					if tokens[i+1][0:11] and tokens[i+3][0:11] == "expression ": #are those variables?
						if eval(tokens[i+1][11:]) == eval(tokens[i+3][11:]): #do them match?
							match = True
					#if tokens[i+1][0:4] and tokens[i+3][0:4] == "var ": #are those variables?
					#	if value(tokens[i+1][4:]) == value(tokens[i+3][4:]): #do them match?
					#		match = True
					i += 5

		#tab
		elif tokens[i] == "tab":
			#create a list starting from a specific point, marked with "tab"
			element = list(islice(dropwhile(lambda x: x != "tab", cycle(tokens)), tokens.index("endif") - tokens.index("tab")))
			#cycle in each character
			for c in element:
				#if it's equal to a tab, remove it otherwise it will break the parser
				if c == "tab":
					element.pop(element.index("tab"))
			#if the elements in the operation match, parse the elements
			try:
				if match == True:
					match = False
					parse(element)
			except:
				continue

		#IMPORT FUNCTION: WIP
		#try:
		#	if tokens[i] + " " + tokens[i+1][0:8] == "import string \"":
		#		if tokens[i+1][0:8] == "string \"": #is it a string?
		#			print("Imported: " + tokens[i+1][8:])
		#		i += 2
		#except:
		#	return

#finally, execute code
run()
