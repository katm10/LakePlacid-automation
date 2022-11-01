from enum import Enum
import os
from typing import Iterator

GCCStage = Enum("GCCStage", ["PREPROCESS", "COMPILE", "ASSEMBLE", "LINK", "UNSPECIFIED"])
InputType = Enum("InputType", ["FILE", "DIR", "OTHER", "NONE"])

class GCCOptionInfo:
  def __init__(self, option: str, double_dash: bool, has_arg: bool, arg_separator: str, input_type: InputType, stage: GCCStage):
    self.option = option
    self.double_dash = double_dash
    self.has_arg = has_arg
    self.arg_separator = arg_separator
    self.input_type = input_type
    self.stage = stage

GCCOptionInfos = [
  # Overall
  GCCOptionInfo("c", False, False, "", InputType.NONE, GCCStage.COMPILE),
  GCCOptionInfo("S", False, False, "", InputType.NONE, GCCStage.COMPILE),
  GCCOptionInfo("o", False, True, " ", InputType.NONE, GCCStage.LINK),
  GCCOptionInfo("x", False, True, " ", InputType.NONE, GCCStage.UNSPECIFIED),

  # Preprocessor
  GCCOptionInfo("Aquestion", False, True, "=", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("A-question", False, True, "=", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("C", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("dD", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("dI", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("dM", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("dN", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("D", False, True, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("H", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("E", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("idirafter", False, True, " ", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("include", False, True, " ", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("imacros", False, True, " ", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("iprefix", False, True, " ", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("iwithprefix", False, True, " ", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("iwithprefixbefore", False, True, " ", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("isystem", False, True, " ", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("M", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("MM", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("MF", False, True, " ", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("MG", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("MP", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("MT", False, True, " ", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("MQ", False, True, " ", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("nostdinc", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("P", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("U", False, True, "", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("Wp", False, True, ",", InputType.NONE, GCCStage.PREPROCESS),
  GCCOptionInfo("Xpreprocessor", False, True, " ", InputType.NONE, GCCStage.PREPROCESS),

  # Warning
  GCCOptionInfo("pedantic", False, False, "", InputType.NONE, GCCStage.COMPILE),
  GCCOptionInfo("pedantic-errors", False, False, "", InputType.NONE, GCCStage.COMPILE),
  GCCOptionInfo("W", False, True, "", InputType.NONE, GCCStage.COMPILE),
  
  # Optimization
  GCCOptionInfo("O", False, True, "", InputType.NONE, GCCStage.COMPILE),
  GCCOptionInfo("Os", False, False, "", InputType.NONE, GCCStage.COMPILE),
  GCCOptionInfo("f", False, True, "", InputType.NONE, GCCStage.COMPILE),
  GCCOptionInfo("param", False, True, "=", InputType.NONE, GCCStage.COMPILE),

  # Assembler
  GCCOptionInfo("Wa", False, True, ",", InputType.NONE, GCCStage.ASSEMBLE),
  GCCOptionInfo("Xassembler", False, True, " ", InputType.NONE, GCCStage.ASSEMBLE),
  
  # Linker
  GCCOptionInfo("l", False, True, "", InputType.NONE, GCCStage.LINK),
  GCCOptionInfo("pie", False, False, "", InputType.NONE, GCCStage.LINK),
  GCCOptionInfo("s", False, False, "", InputType.NONE, GCCStage.LINK),
  GCCOptionInfo("static", False, False, "", InputType.NONE, GCCStage.LINK),
  GCCOptionInfo("shared", False, False, "", InputType.NONE, GCCStage.LINK),
  GCCOptionInfo("Wl", False, True, ",", InputType.NONE, GCCStage.LINK),
  GCCOptionInfo("Xlinker", False, True, " ", InputType.NONE, GCCStage.LINK),
  GCCOptionInfo("u", False, True, "", InputType.NONE, GCCStage.LINK),

  # Directory
  GCCOptionInfo("B", False, True, " ", InputType.NONE, GCCStage.UNSPECIFIED),
  GCCOptionInfo("Idir", False, True, " ", InputType.NONE, GCCStage.UNSPECIFIED),
  GCCOptionInfo("I-", False, False, "", InputType.NONE, GCCStage.UNSPECIFIED),
  GCCOptionInfo("L", False, True, " ", InputType.NONE, GCCStage.UNSPECIFIED),
  GCCOptionInfo("specs", False, True, " ", InputType.NONE, GCCStage.UNSPECIFIED)
]

class GCCTarget: 
  def __init__(self, target):
    self.target = target
    self.abs_target = None

    if os.path.exists(self.target):
      self.abs_target = os.path.abspath(self.target)
      if os.path.isdir: 
        self.input_type = InputType.DIRECTORY
      else:
        self.input_type = InputType.FILE
    else:
      self.input_type = InputType.OTHER
  

class GCCOption:
  def __init__(self):
    pass

  @staticmethod
  def find_matching_arg(option: str, double_dash: bool) -> GCCOptionInfo:
    for info in GCCOptionInfos:
      if info.double_dash == double_dash and option.startswith(info):
        return info
    return None

  @staticmethod
  def construct(option: str, option_info: GCCOptionInfo, arg_iter: Iterator[str]) -> GCCOption:
    if option_info.has_arg:
      if option_info.arg_separator == " ":
        arg = next(arg_iter)
      else:
        arg = option.split(option_info.arg_separator)[1]
      
      if option_info.input_type == InputType.FILE or option_info.input_type == InputType.DIR:
        arg = GCCTarget(arg)
    return GCCOption()
