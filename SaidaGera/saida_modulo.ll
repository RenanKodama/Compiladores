; ModuleID = "programaTpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"func"(i32 %".1", float %".2") 
{
entry:
  %"r" = alloca i32, align 4
  br label %"exit"
exit:
  ret i32* %"r"
}

define i32 @"principal"() 
{
entry:
  %"x" = alloca i32, align 4
  %".2" = load i32 (i32, float), i32 (i32, float)* @"func"
  br label %"exit"
exit:
  ret i32 0
}
