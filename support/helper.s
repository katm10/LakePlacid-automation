.extern  __translate_function_
.extern mpns_abort
.extern translate_return_addr

.section .text
  .global mpns_likely
  .global mpns_unlikely
  .global translate_return

translate_return:
  # happens after register allocation, save everything
  push %rax
  push %rbp
  push %rdi
  push %rsi
  push %r12

  # update rsp
  mov %rsp, %r12
  mov 0x28(%r12), %rdi
  call translate_return_addr
  mov %rax, (%r12)

  # restore everything
  pop %r12
  pop %rsi
  pop %rdi
  pop %rbp
  pop %rax

  ret

mpns_likely:
  # called with mpns_likely(int condition, char* name, int id, void* fn)

  # Params: %rdi = condition, %rsi = name, %rdx = id, %rcx = fn
  mov %rsp, %r12
  push %rbp
  push %rdi
  push %rsi
  mov %rsp, %rbp
  cmp $0, %rdi
  jne .done_likely

  mov %rcx, %rdi
  mov (%r12), %rsi
  call mpns_abort
  mov %rax, (%r12) # store new ip

.done_likely:
  pop %rsi # just for alignment
  # return the condition
  pop %rax
  pop %rbp
  ret

mpns_unlikely:
  # called with mpns_unlikely(int condition, char* name, int id, void* fn)

  # Params: %rdi = condition, %rsi = name, %rdx = id, %rcx = fn
  mov %rsp, %r12
  push %rbp
  push %rdi
  push %rsi
  mov %rsp, %rbp
  cmp $0, %rdi
  je .done_unlikely
  
  mov %rcx, %rdi
  mov (%r12), %rsi
  call mpns_abort
  mov %rax, (%r12) # store new ip

.done_unlikely:
  pop %rsi # just for alignment
  # return the condition
  pop %rax
  pop %rbp
  ret


