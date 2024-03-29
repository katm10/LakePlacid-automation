from enum import Enum
from typing import Tuple
from dataclasses import dataclass

GCCStage = Enum(
    "GCCStage",
    [
        "PREPROCESS",
        "COMPILE",
        "ASSEMBLE",
        "LINK",
        "INSTRUMENT",
        "UNSPECIFIED",
        "UNUSED",
    ],
)
InputType = Enum("InputType", ["FILE", "DIR", "OTHER", "NONE"])


@dataclass
class GCCOptionInfo:
    option: str
    double_dash: bool
    has_arg: bool
    arg_separator: str
    input_type: InputType
    stage: GCCStage


GCCOptionInfos = [
    # Overall
    GCCOptionInfo("c", False, False, "", InputType.NONE, GCCStage.COMPILE),
    GCCOptionInfo("S", False, False, "", InputType.NONE, GCCStage.COMPILE),
    GCCOptionInfo("o", False, True, " ", InputType.NONE, GCCStage.LINK),
    GCCOptionInfo("x", False, True, " ", InputType.NONE, GCCStage.UNSPECIFIED),
    # To ignore
    GCCOptionInfo("MM", False, False, "", InputType.NONE, GCCStage.UNUSED),
    GCCOptionInfo("flto", False, False, "", InputType.NONE, GCCStage.UNUSED),
    GCCOptionInfo("MF", False, True, " ", InputType.FILE, GCCStage.UNUSED),
    GCCOptionInfo("MG", False, False, "", InputType.NONE, GCCStage.UNUSED),
    GCCOptionInfo("MP", False, False, "", InputType.NONE, GCCStage.UNUSED),
    GCCOptionInfo("MT", False, True, " ", InputType.FILE, GCCStage.UNUSED),
    GCCOptionInfo("MQ", False, True, " ", InputType.FILE, GCCStage.UNUSED),
    GCCOptionInfo("M", False, False, "", InputType.NONE, GCCStage.UNUSED),
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
    GCCOptionInfo(
        "iwithprefixbefore", False, True, " ", InputType.NONE, GCCStage.PREPROCESS
    ),
    GCCOptionInfo("isystem", False, True, " ", InputType.NONE, GCCStage.PREPROCESS),
    GCCOptionInfo("nostdinc", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
    GCCOptionInfo("P", False, False, "", InputType.NONE, GCCStage.PREPROCESS),
    GCCOptionInfo("U", False, True, "", InputType.NONE, GCCStage.PREPROCESS),
    GCCOptionInfo("Wp", False, True, ",", InputType.NONE, GCCStage.PREPROCESS),
    GCCOptionInfo(
        "Xpreprocessor", False, True, " ", InputType.NONE, GCCStage.PREPROCESS
    ),
    GCCOptionInfo("I", False, True, "", InputType.DIR, GCCStage.PREPROCESS),
    # Warning
    GCCOptionInfo("pedantic", False, False, "", InputType.NONE, GCCStage.UNUSED),
    GCCOptionInfo(
        "pedantic-errors", False, False, "", InputType.NONE, GCCStage.COMPILE
    ),
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
    GCCOptionInfo("specs", False, True, " ", InputType.NONE, GCCStage.UNSPECIFIED),
]


@dataclass
class GCCOption:
    stage: GCCStage
    option: str
    target: str
    target_type: InputType
    separator: str

    def to_json(self):
        return {
            "option": self.option,
            "target": self.target,
            "target_type": self.target_type.name,
            "separator": self.separator,
        }

    @staticmethod
    def find_matching_arg(option: str, double_dash: bool) -> GCCOptionInfo:
        for info in GCCOptionInfos:
            if info.double_dash == double_dash and option.startswith(info.option):
                return info
        return None

    @staticmethod
    def construct(option: str, indx: int, args: list) -> Tuple["GCCOption", int]:
        double_dash = False
        if option.startswith("--"):
            flag = option[2:]
            double_dash = True
        else:
            flag = option[1:]

        arg = None
        option_info = GCCOption.find_matching_arg(flag, double_dash)
        if option_info is None:
            return (
                GCCOption(GCCStage.UNSPECIFIED, option, None, InputType.NONE, ""),
                indx,
            )

        if option_info.has_arg:
            if option_info.arg_separator == " ":
                indx += 1
                arg = args[indx]
            elif option_info.arg_separator == "":
                arg_indx = (double_dash and 2 or 1) + len(option_info.option)
                arg = option[arg_indx:]
                option = option[:arg_indx]
            else:
                arg = option.split(option_info.arg_separator)[1]

        return (
            GCCOption(
                option_info.stage,
                option,
                arg,
                option_info.input_type,
                option_info.arg_separator,
            ),
            indx,
        )

    @staticmethod
    def from_json(option, stage):
        return GCCOption(
            stage,
            option["option"],
            option["target"],
            InputType[option["target_type"]],
            option["separator"],
        )
