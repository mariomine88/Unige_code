open Semantics
let prog=MyLangProg(NonEmptyStmtSeq(PrintStmt(DictPut(DictPut(DictCons(IntLiteral 3,PairLit(IntLiteral 5,IntLiteral 0)),IntLiteral 2,PairLit(IntLiteral 4,IntLiteral 1)),IntLiteral 1,PairLit(IntLiteral 3,IntLiteral 2))),EmptyStmtSeq))
typecheckProg prog
executeProg prog
