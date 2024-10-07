package progetto2024.parser;


public enum TokenType {
	// used internally by the tokenizer, should never been accessed by the parser
	SYMBOL, KEYWORD, SKIP, 
	// non singleton categories
	IDENT, NUM,   
	// end-of-file
	EOF, 	
	// symbols
	ASSIGN, MINUS, PLUS, TIMES, NOT, AND, EQ, STMT_SEP, DICT_OP, PAIR_OP, OPEN_PAR, CLOSE_PAR, OPEN_DICT, CLOSE_DICT, OPEN_BLOCK, CLOSE_BLOCK,
	// keywords
	PRINT, VAR, BOOL, IF, ELSE, FOR, OF, FST, SND,
}
