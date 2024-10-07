module Semantics

(* environments *)

type variable = Name of string

type 'a scope = Map<variable, 'a>

type 'a environment = 'a scope list

exception UndeclaredVariable of variable

exception AlreadyDeclaredVariable of variable
let emptyScope: 'a scope = Map.empty
let initialEnv: 'a environment = [ emptyScope ] (* the empty top-level scope *)

(* enterScope: 'a environment -> 'a environment *)

let enterScope (env: 'a environment) : 'a environment =
    emptyScope :: env (* enters a new nested scope *)

(* exitScope only needed for the dynamic semantics *)

(* exitScope: 'a environment -> 'a environment *)

let exitScope: 'a environment -> 'a environment =
    function (* removes the innermost scope, only needed for the dynamic semantics *)
    | _ :: env -> env
    | [] -> failwith "assertion error" (* should never happen *)

(* variable lookup *)

(* lookup uses Map.tryFind
   examples:

let sEnv: staticType scope =
    Map.add (Name "x") IntType Map.empty |> Map.add (Name "y") BoolType

assert (Map.tryFind (Name "x") sEnv = Some IntType)
assert (Map.tryFind (Name "y") sEnv = Some BoolType)
assert (Map.tryFind (Name "z") sEnv = None)

let dEnv: value scope =
    Map.add (Name "x") (IntValue 3) Map.empty
    |> Map.add (Name "y") (BoolValue false)

assert (Map.tryFind (Name "x") dEnv = Some(IntValue 3))
assert (Map.tryFind (Name "y") dEnv = Some(BoolValue false))
assert (Map.tryFind (Name "z") dEnv = None)

*)

(* lookup: variable -> environment<'a> -> 'a *)

let rec lookup (var) : 'a environment -> 'a =
    function
    | scope :: env ->
        match Map.tryFind var scope with
        | Some res -> res
        | _ -> lookup var env // None is the only possible value
    | [] -> raise (UndeclaredVariable var)

(* variable declaration *)

(* example:
   dec x ty env1 = env2 means that 'env2' is the new environment after declaring variable 'x' of type 'ty' in the environment 'env1'
   dec x value env1 = env2 means that 'env2' is the new environment after declaring variable 'x' initialized with value 'value' in the environment 'env1'
*)

(* dec uses Map.containsKey *)

(* dec: variable -> 'a -> environment<'a> -> environment<'a> *)

let dec (var) (info) : 'a environment -> 'a environment =
    function
    | scope :: env ->
        if Map.containsKey var scope then
            raise (AlreadyDeclaredVariable var)
        else
            (Map.add var info scope) :: env
    | [] -> failwith "assertion error" (* should never happen *)

(* variable update, only needed for the dynamic semantics *)

(* update uses Map.containsKey *)

(* update: variable -> 'a -> environment<'a> -> environment<'a> *)

let rec update (var) (info) : 'a environment -> 'a environment =
    function
    | scope :: env ->
        if (Map.containsKey var scope) then
            (Map.add var info scope) :: env
        else
            scope :: update var info env
    | [] -> raise (UndeclaredVariable var)


(* static semantics of the language *)

(* AST of expressions *)

type exp =
    | Add of exp * exp
    | Mul of exp * exp
    | And of exp * exp
    | Eq of exp * exp
    | PairLit of exp * exp
    | Fst of exp
    | Snd of exp
    | Sign of exp
    | Not of exp
    | IntLiteral of int
    | BoolLiteral of bool
    | Var of variable
    | DictCons of exp * exp
    | DictDel of exp * exp
    | DictGet of exp * exp
    | DictPut of exp * exp * exp

(* AST of statements and sequence of statements, mutually recursive *)

type stmt =
    | AssignStmt of variable * exp
    | VarStmt of variable * exp
    | PrintStmt of exp
    | IfStmt of exp * block * block
    | ForStmt of variable * exp * block

and block =
    | EmptyBlock
    | Block of stmtSeq

and stmtSeq =
    | EmptyStmtSeq
    | NonEmptyStmtSeq of stmt * stmtSeq

(* AST of programs *)
type prog = MyLangProg of stmtSeq

(* static types *)

type staticType =
    | IntType
    | BoolType
    | PairType of staticType * staticType
    | DictType of staticType

(* examples
    PairType(IntType,BoolType) corresponds to int * bool
    PairType(IntType,PairType(IntType,BoolType)) corresponds to int * (int * bool)
*)

type staticEnv = staticType environment

(* static errors *)

exception ExpectingTypeFoundError of staticType * staticType

exception ExpectingPairError of staticType

exception ExpectingDictError of staticType

let getValueType =
    function
    | DictType valueType -> valueType
    | found -> raise (ExpectingDictError found) 

(* static semantic functions *)


(* static semantic functions *)


(*
    typecheckExp: staticEnv -> exp -> staticType
    typecheckType: staticType -> staticEnv -> exp -> staticType
    mutually recursive functions, typecheckType auxiliary
*)

(* typecheckExp env exp = ty means that expressions 'exp' is type correct in the environment 'env' and has static type 'ty' *)
(* typecheckType expectedTy env exp = ty means that 'exp' has type 'ty' in 'env' and 'ty'='expectedTy' *)
let rec typecheckExp (env: staticEnv) =
    function
    | Add (exp1, exp2)
    | Mul (exp1, exp2) ->
        typecheckHasType IntType env exp1 |> ignore // returned type value ignored
        typecheckHasType IntType env exp2
    | And (exp1, exp2) ->
        typecheckHasType BoolType env exp1 |> ignore
        typecheckHasType BoolType env exp2
    | Eq (exp1, exp2) ->
        let type1 = typecheckExp env exp1
        typecheckHasType type1 env exp2 |> ignore
        BoolType
    | PairLit (exp1, exp2) ->
        let type1 = typecheckExp env exp1
        let type2 = typecheckExp env exp2
        PairType(type1, type2)
    | Fst exp ->
        match typecheckExp env exp with
        | PairType (type1, _) -> type1
        | found -> raise (ExpectingPairError found)
    | Snd exp ->
        match typecheckExp env exp with
        | PairType (_, type2) -> type2
        | found -> raise (ExpectingPairError found)
    | Sign exp -> typecheckHasType IntType env exp
    | Not exp -> typecheckHasType BoolType env exp
    | IntLiteral _ -> IntType
    | BoolLiteral _ -> BoolType
    | Var var -> lookup var env
    | DictCons (exp1, exp2) ->
        typecheckHasType IntType env exp1 |> ignore
        DictType(typecheckExp env exp2)
    | DictDel (exp1, exp2) ->
        let dictType = typecheckDict env exp1
        typecheckHasType IntType env exp2 |> ignore
        dictType
    | DictGet (exp1, exp2) ->
        let dictType = typecheckDict env exp1
        typecheckHasType IntType env exp2 |> ignore
        getValueType dictType
    | DictPut (exp1, exp2, exp3) ->
        let dictType = typecheckDict env exp1
        let valueType = getValueType dictType
        typecheckHasType IntType env exp2 |> ignore
        typecheckHasType valueType env exp3 |> ignore
        dictType

(* auxiliary functions for typeCheckExp *)

and typecheckHasType expectedTy env exp =
    let foundType = typecheckExp env exp

    if foundType = expectedTy then
        foundType
    else
        raise (ExpectingTypeFoundError (expectedTy,foundType))

and typecheckDict env exp =
    let dictType = typecheckExp env exp

    match dictType with
    | DictType _ -> dictType
    | found -> raise (ExpectingDictError found)

(* mutually recursive functions

 typecheckStmt : staticEnv -> stmt -> staticEnv
 typecheckBlock : staticEnv -> block -> unit
 typecheckStmtSeq : staticEnv -> stmtSeq -> unit

*)

(* typecheckStmt env1 st = env2 means that statement 'st' is type correct in the environment 'env1' and defines the new environment 'env2' *)
(* typecheckBlock env block = () means that the block 'block' is type correct in the environment 'env' *)
(* typecheckStmtSeq env1 stSeq = env2 means that statement sequence 'stSeq' is type correct in the environment 'env1' and defines the new environment 'env2' *)

let rec typecheckStmt (env: staticEnv) =
    function
    | AssignStmt (var, exp) ->
        let type1 = lookup var env
        typecheckHasType type1 env exp |> ignore
        env
    | VarStmt (var, exp) -> dec var (typecheckExp env exp) env
    | PrintStmt exp ->
        typecheckExp env exp |> ignore
        env
    | IfStmt (exp, thenBlock, elseBlock) ->
        typecheckHasType BoolType env exp |> ignore
        typecheckBlock env thenBlock
        typecheckBlock env elseBlock
        env
    | ForStmt (var, exp, block) ->
        let dictType = typecheckDict env exp
        let nestedEnv = enterScope env
        let varType = PairType(IntType, getValueType dictType)
        let forEnv = dec var varType nestedEnv
        typecheckBlock forEnv block
        env

and typecheckBlock env =
    function
    | EmptyBlock -> ()
    | Block stmtSeq ->
        typecheckStmtSeq (enterScope env) stmtSeq
        ()

and typecheckStmtSeq (env: staticEnv) =
    function
    | EmptyStmtSeq -> ()
    | NonEmptyStmtSeq (stmt, stmtSeq) -> typecheckStmtSeq (typecheckStmt env stmt) stmtSeq

(*
  typecheckProg : prog -> unit
*)

(* typecheckProg p = () means that program 'p' is well defined with respect to the static semantics *)

let typecheckProg =
    function
    | MyLangProg stmtSeq ->
        typecheckStmtSeq initialEnv stmtSeq
        ()

(* dynamic semantics of the language *)

(* values *)

type value =
    | IntValue of int
    | BoolValue of bool
    | PairValue of value * value
    | DictValue of Map<int, value>

(* examples
    PairLit(IntLiteral 2,BoolLiteral false) corresponds to  2,false
    PairLit(IntLiteral 2,PairLit(IntLiteral 3,BoolLiteral true)) corresponds to 2,(3,true)
*)

type dynamicEnv = value environment

(* dynamic errors *)

exception ExpectingDynTypeError of string (* dynamic conversion error *)

exception MissingKey of int (* dynamic error raised when trying to get or delete a missing key *)

let checkKey key map =
    if Map.containsKey key map then
        ()
    else
        raise (MissingKey key)
(* auxiliary functions *)

(* dynamic conversion to int type *)
(* toInt : value -> int *)

let toInt =
    function
    | IntValue i -> i
    | _ -> raise (ExpectingDynTypeError "int")

(* dynamic conversion to bool type *)
(* toBool : value -> bool *)

let toBool =
    function
    | BoolValue b -> b
    | _ -> raise (ExpectingDynTypeError "bool")

(* toPair : value -> value * value *)
(* dynamic conversion to product  type *)

let toPair =
    function
    | PairValue (e1, e2) -> e1, e2
    | _ -> raise (ExpectingDynTypeError "pair")

let toMap =
    function
    | DictValue m -> m
    | _ -> raise (ExpectingDynTypeError "dict")

(* fst and snd operators *)
(* fst: 'a * 'b -> 'a  and snd: 'a * 'b -> 'b predefined in F# *)

(* conversion to string *)

(* toString : value -> string *)

let rec toString =
    function (* uses interpolated strings *)
    | IntValue i -> $"{i}"
    | BoolValue true -> "true"
    | BoolValue false -> "false"
    | PairValue (v1, v2) -> $"({toString v1},{toString v2})"
    | DictValue m ->
        let separator acc = if acc = "" then "" else ","

        let s =
            m
            |> Map.fold (fun acc key value -> $"{acc}{separator acc}{key}:{toString value}") ""

        "[" + s + "]"

(* printing function *)

(* printf "%s": string -> unit predefined in F# *)

(* evalExp : dynamicEnv -> exp -> value *)
(* evalExp env exp = val means that expressions 'exp' successfully evaluates to 'val' in the environment 'env' *)

let rec evalExp (env: dynamicEnv) =
    function
    | Add (exp1, exp2) ->
        (evalExp env exp1 |> toInt)
        + (evalExp env exp2 |> toInt)
        |> IntValue
    | Mul (exp1, exp2) ->
        (evalExp env exp1 |> toInt)
        * (evalExp env exp2 |> toInt)
        |> IntValue
    | And (exp1, exp2) ->
        ((evalExp env exp1 |> toBool)
         && (evalExp env exp2 |> toBool))
        |> BoolValue
    | Eq (exp1, exp2) -> evalExp env exp1 = evalExp env exp2 |> BoolValue
    | PairLit (exp1, exp2) -> (evalExp env exp1, evalExp env exp2) |> PairValue
    | Fst exp -> evalExp env exp |> toPair |> fst
    | Snd exp -> evalExp env exp |> toPair |> snd
    | Sign exp -> evalExp env exp |> toInt |> (~-) |> IntValue // (~-) is the unary minus
    | Not exp -> evalExp env exp |> toBool |> (not) |> BoolValue
    | IntLiteral i -> IntValue i
    | BoolLiteral b -> BoolValue b
    | Var var -> lookup var env
    | DictCons (exp1, exp2) ->
        Map.add (evalExp env exp1 |> toInt) (evalExp env exp2) Map.empty
        |> DictValue
    | DictDel (exp1, exp2) ->
        let m = evalExp env exp1 |> toMap
        let k = evalExp env exp2 |> toInt
        checkKey k m
        Map.remove k m |> DictValue
    | DictGet (exp1, exp2) ->
        let m = evalExp env exp1 |> toMap
        let k = evalExp env exp2 |> toInt
        checkKey k m
        Map.find k m
    | DictPut (exp1, exp2, exp3) ->
        let m = evalExp env exp1 |> toMap
        let k = evalExp env exp2 |> toInt
        Map.add k (evalExp env exp3) m |> DictValue

(* mutually recursive
   executeStmt : dynamicEnv -> stmt -> dynamicEnv
   executeBlock : dynamicEnv -> block -> dynamicEnv
   executeStmtSeq : dynamicEnv -> stmtSeq -> dynamicEnv
*)

(* executeStmt env1 'stmt' = env2 means that the execution of statement 'stmt' in environment 'env1' successfully returns the new environment 'env2' *)
(* executeBlock env1 block = env2 means that the execution of block 'block' in environment 'env1' successfully returns the new environment 'env2' *)
(* executeStmtSeq env1 stmtSeq = env2 means that the execution of sequence 'stmtSeq' in environment 'env1' successfully returns the new environment 'env2' *)
(* executeStmt, executeBlock and executeStmtSeq write on the standard output if some 'print' statement is executed *)

let rec executeStmt (env) : stmt -> dynamicEnv =
    function
    | AssignStmt (var, exp) -> update var (evalExp env exp) env
    | VarStmt (var, exp) -> dec var (evalExp env exp) env
    | PrintStmt exp ->
        evalExp env exp |> toString |> printfn "%s"
        env
    | IfStmt (exp, thenBlock, elseBlock) ->
        if toBool (evalExp env exp) then
            executeBlock env thenBlock
        else
            executeBlock env elseBlock
    | ForStmt (var, exp, block) ->
        let m = evalExp env exp |> toMap
        let forEnv = enterScope env |> dec var (IntValue 0)

        let loop env key value =
            (update var (PairValue(IntValue key, value)) env
             |> executeBlock)
                block

        m |> Map.fold loop forEnv

and executeBlock env =
    function (* note the differences with the static semantics *)
    | EmptyBlock -> env
    | Block stmtSeq ->
        executeStmtSeq (enterScope env) stmtSeq
        |> exitScope

and executeStmtSeq (env: dynamicEnv) : stmtSeq -> dynamicEnv =
    function
    | EmptyStmtSeq -> env
    | NonEmptyStmtSeq (stmt, stmtSeq) -> executeStmtSeq (executeStmt env stmt) stmtSeq


(* executeProg : prog -> unit *)
(* executeProg prog = () means that program 'prog' has been executed successfully, by possibly writing on the standard output *)

let executeProg =
    function
    | MyLangProg stmtSeq ->
        executeStmtSeq initialEnv stmtSeq |> ignore
        ()
