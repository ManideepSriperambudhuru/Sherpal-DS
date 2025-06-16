import json

class DifficultyType():
    EASY = "EAS"
    MEDIUM = "MED"
    HARD = "HAR"
    VERY_HARD = "VHA"

    __LABELS__ = {
        "EASY": "Easy",
        "MEDIUM": "Medium",
        "HARD": "Hard",
        "VERY_HARD": "Very Hard",
    }

    @staticmethod
    def get_difficulty(difficulty_value):
        for key, value in DifficultyType.__LABELS__.items():
            if value == difficulty_value:
                difficulty_value = DifficultyType.get_name_by_value(DifficultyType[key].value)
                return difficulty_value
        return None

    @staticmethod
    def get_difficulty_values(exclude_VHA=False):
        difficulty_types = []
        for value in DifficultyType.__LABELS__.values():
            if value == "Very Hard" and exclude_VHA:
                continue
            difficulty_types.append(value)
        return difficulty_types

class SkillType():
    # RW Skills
    CAS_WIC = (
        "Words in Context",
        "RW",
        {DifficultyType.EASY: 9.35, DifficultyType.MEDIUM: 3.96, DifficultyType.HARD: 3.85},
        17.16,
        [
            "https://www.khanacademy.org/test-prep/sat-reading-and-writing/x0d47bcec73eb6c4b:foundations-craft-and-structure/x0d47bcec73eb6c4b:words-in-context/a/words-in-context-lesson"
        ],
    )
    SEC_BND = (
        "Boundaries",
        "RW",
        {DifficultyType.EASY: 3.96, DifficultyType.MEDIUM: 3.64, DifficultyType.HARD: 6.31},
        13.91,
        [
            "https://www.khanacademy.org/test-prep/sat-reading-and-writing/x0d47bcec73eb6c4b:foundations-expression-of-ideas-and-standard-english-conventions/x0d47bcec73eb6c4b:boundaries/a/boundaries-overview"
        ],
    )
    SEC_FSS = (
        "Form, Structure, and Sense",
        "RW",
        {DifficultyType.EASY: 6.63, DifficultyType.MEDIUM: 3.00, DifficultyType.HARD: 2.46},
        12.09,
        [
            "https://www.khanacademy.org/test-prep/sat-reading-and-writing/x0d47bcec73eb6c4b:foundations-expression-of-ideas-and-standard-english-conventions/x0d47bcec73eb6c4b:form-structure-and-sense/a/form-structure-and-sense-overview"
        ],
    )
    EOI_RHS = (
        "Rhetorical Synthesis",
        "RW",
        {DifficultyType.EASY: 1.13, DifficultyType.MEDIUM: 7.43, DifficultyType.HARD: 2.35},
        10.90,
        [
            "https://www.khanacademy.org/test-prep/sat-reading-and-writing/x0d47bcec73eb6c4b:foundations-expression-of-ideas-and-standard-english-conventions/x0d47bcec73eb6c4b:rhetorical-synthesis/a/rhetorical-synthesis-lesson"
        ],
    )
    EOI_TRN = (
        "Transitions",
        "RW",
        {DifficultyType.EASY: 4.32, DifficultyType.MEDIUM: 3.76, DifficultyType.HARD: 1.50},
        9.59,
        [
            "https://www.khanacademy.org/test-prep/sat-reading-and-writing/x0d47bcec73eb6c4b:foundations-expression-of-ideas-and-standard-english-conventions/x0d47bcec73eb6c4b:transitions/a/transitions-lesson"
        ],
    )
    IAI_COT = (
        "Command of Evidence - Textual",
        "RW",
        {DifficultyType.EASY: 1.80, DifficultyType.MEDIUM: 2.79, DifficultyType.HARD: 4.50},
        9.09,
        [
            "https://www.khanacademy.org/test-prep/sat-reading-and-writing/x0d47bcec73eb6c4b:foundations-information-and-ideas/x0d47bcec73eb6c4b:command-of-evidence-textual/a/command-of-evidence-textual-lesson"
        ],
    )
    CAS_TSP = (
        "Text Structure and Purpose",
        "RW",
        {DifficultyType.EASY: 1.32, DifficultyType.MEDIUM: 3.96, DifficultyType.HARD: 2.75},
        8.03,
        [
            "https://www.khanacademy.org/test-prep/sat-reading-and-writing/x0d47bcec73eb6c4b:foundations-craft-and-structure/x0d47bcec73eb6c4b:text-structure-and-purpose/a/text-structure-and-purpose-lesson"
        ],
    )
    IAI_CID = (
        "Central Ideas and Details",
        "RW",
        {DifficultyType.EASY: 1.17, DifficultyType.MEDIUM: 3.06, DifficultyType.HARD: 2.07},
        6.30,
        [
            "https://www.khanacademy.org/test-prep/sat-reading-and-writing/x0d47bcec73eb6c4b:foundations-information-and-ideas/x0d47bcec73eb6c4b:central-ideas-and-details/a/central-ideas-and-details-lesson"
        ],
    )
    IAI_INF = (
        "Inferences",
        "RW",
        {DifficultyType.EASY: 0.36, DifficultyType.MEDIUM: 2.52, DifficultyType.HARD: 3.33},
        6.21,
        [
            "https://www.khanacademy.org/test-prep/sat-reading-and-writing/x0d47bcec73eb6c4b:foundations-information-and-ideas/x0d47bcec73eb6c4b:inferences/a/inferences-lesson"
        ],
    )
    IAI_COQ = (
        "Command of Evidence - Quantitative",
        "RW",
        {DifficultyType.EASY: 0.27, DifficultyType.MEDIUM: 1.80, DifficultyType.HARD: 2.34},
        4.41,
        [
            "https://www.khanacademy.org/test-prep/sat-reading-and-writing/x0d47bcec73eb6c4b:foundations-information-and-ideas/x0d47bcec73eb6c4b:command-of-evidence-quantitative/a/command-of-evidence-quantitative-lesson"
        ],
    )
    CAS_XTC = (
        "Cross-text Connections",
        "RW",
        {DifficultyType.EASY: 0.11, DifficultyType.MEDIUM: 0.99, DifficultyType.HARD: 0.21},
        2.31,
        [
            "https://www.khanacademy.org/test-prep/sat-reading-and-writing/x0d47bcec73eb6c4b:foundations-craft-and-structure/x0d47bcec73eb6c4b:cross-text-connections/a/cross-text-connections-lesson"
        ],
    )

    # Math Skills
    ADM_NLF = (
        "Nonlinear functions",
        "Math",
        {DifficultyType.EASY: 5.16, DifficultyType.MEDIUM: 6.36, DifficultyType.HARD: 7.20},
        18.72,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:advanced-math-easier/x0fcc98a58ba3bea7:nonlinear-functions-easier/a/v2-sat-lesson-nonlinear-functions"
        ],
    )
    ADM_NLE = (
        "Nonlinear equations in one variable and systems of equations in two variables",
        "Math",
        {DifficultyType.EASY: 2.50, DifficultyType.MEDIUM: 2.90, DifficultyType.HARD: 3.60},
        10.80,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:advanced-math-easier/x0fcc98a58ba3bea7:linear-and-quadratic-systems-easier/a/v2-sat-lesson-linear-and-quadratic-systems"
        ],
    )
    ALG_LIF = (
        "Linear functions",
        "Math",
        {DifficultyType.EASY: 6.11, DifficultyType.MEDIUM: 3.49, DifficultyType.HARD: 0.87},
        10.48,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:algebra-easier/x0fcc98a58ba3bea7:linear-relationship-word-problems-easier/a/v2-sat-lesson-understanding-linear-relationships"
        ],
    )
    ALG_LET = (
        "Linear equations in two variables",
        "Math",
        {DifficultyType.EASY: 3.88, DifficultyType.MEDIUM: 2.04, DifficultyType.HARD: 2.23},
        8.15,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:algebra-easier/x0fcc98a58ba3bea7:systems-of-linear-equations-word-problems-easier/a/v2-sat-lesson-systems-of-linear-equations-word-problems"
        ],
    )
    ALG_SLE = (
        "Systems of two linear equations in two variables",
        "Math",
        {DifficultyType.EASY: 2.04, DifficultyType.MEDIUM: 2.43, DifficultyType.HARD: 2.43},
        6.89,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:algebra-easier/x0fcc98a58ba3bea7:solving-systems-of-linear-equations-easier/a/v2-sat-lesson-solving-systems-of-linear-equations"
        ],
    )
    ADM_EQE = (
        "Equivalent expressions",
        "Math",
        {DifficultyType.EASY: 2.88, DifficultyType.MEDIUM: 1.92, DifficultyType.HARD: 1.32},
        6.12,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:advanced-math-easier/x0fcc98a58ba3bea7:isolating-quantities-easier/a/v2-sat-lesson-isolating-quantities"
        ],
    )
    ALG_LEO = (
        "Linear equations in one variable",
        "Math",
        {DifficultyType.EASY: 4.27, DifficultyType.MEDIUM: 0.87, DifficultyType.HARD: 0.87},
        6.01,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:algebra-easier/x0fcc98a58ba3bea7:solving-linear-equations-and-inequalities-easier/a/v2-sat-lesson-solving-linear-equations-and-inequalities"
        ],
    )
    GAT_AAV = (
        "Area and volume",
        "Math",
        {DifficultyType.EASY: 1.89, DifficultyType.MEDIUM: 1.68, DifficultyType.HARD: 1.58},
        5.15,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:geometry-and-trigonometry-easier/x0fcc98a58ba3bea7:area-and-volume-easier/a/v2-sat-lesson-area-and-volume"
        ],
    )
    GAT_LAT = (
        "Lines, angles, and triangles",
        "Math",
        {DifficultyType.EASY: 2.10, DifficultyType.MEDIUM: 0.95, DifficultyType.HARD: 1.47},
        4.52,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:geometry-and-trigonometry-easier/x0fcc98a58ba3bea7:congruence-similarity-and-angle-relationships-easier/a/v2-sat-lesson-congruence-similarity-and-angle-relationships"
        ],
    )
    PSD_RRP = (
        "Ratios, rates, proportional relationships, and units",
        "Math",
        {DifficultyType.EASY: 2.19, DifficultyType.MEDIUM: 1.17, DifficultyType.HARD: 0.58},
        3.94,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:problem-solving-and-data-analysis-easier/x0fcc98a58ba3bea7:ratios-rates-and-proportions-easier/a/v2-sat-lesson-ratios-rates-and-proportions",
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:problem-solving-and-data-analysis-easier/x0fcc98a58ba3bea7:unit-conversion-easier/a/v2-sat-lesson-unit-conversion",
        ],
    )
    ALG_LIN = (
        "Linear inequalities in one or two variables",
        "Math",
        {DifficultyType.EASY: 1.46, DifficultyType.MEDIUM: 1.46, DifficultyType.HARD: 0.87},
        3.78,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:algebra-easier/x0fcc98a58ba3bea7:linear-inequality-word-problems-easier/a/v2-sat-lesson-linear-inequality-word-problems"
        ],
    )
    PSD_PER = (
        "Percentages",
        "Math",
        {DifficultyType.EASY: 1.10, DifficultyType.MEDIUM: 1.02, DifficultyType.HARD: 1.39},
        3.50,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:problem-solving-and-data-analysis-easier/x0fcc98a58ba3bea7:percentages-easier/a/v2-sat-lesson-percentages"
        ],
    )
    PSD_OVD = (
        "One-variable data: Distributions and measures of center and spread",
        "Math",
        {DifficultyType.EASY: 1.46, DifficultyType.MEDIUM: 0.58, DifficultyType.HARD: 1.10},
        3.14,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:problem-solving-and-data-analysis-easier/x0fcc98a58ba3bea7:center-spread-and-shape-of-distributions-easier/a/v2-sat-lesson-center-spread-and-shape-of-distributions"
        ],
    )
    GAT_RTT = (
        "Right triangles and trigonometry",
        "Math",
        {DifficultyType.EASY: 0.63, DifficultyType.MEDIUM: 0.53, DifficultyType.HARD: 1.58},
        2.73,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:geometry-and-trigonometry-easier/x0fcc98a58ba3bea7:right-triangle-trigonometry-easier/a/v2-sat-lesson-right-triangle-trigonometry"
        ],
    )
    PSD_TVD = (
        "Two-variable data: Models and scatterplots",
        "Math",
        {DifficultyType.EASY: 1.46, DifficultyType.MEDIUM: 0.73, DifficultyType.HARD: 0.29},
        2.48,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:problem-solving-and-data-analysis-easier/x0fcc98a58ba3bea7:scatterplots-easier/a/v2-sat-lesson-scatterplots"
        ],
    )
    GAT_CIR = (
        "Circles",
        "Math",
        {DifficultyType.EASY: 0.00, DifficultyType.MEDIUM: 0.42, DifficultyType.HARD: 2.00},
        2.42,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:geometry-and-trigonometry-easier/x0fcc98a58ba3bea7:circle-theorems-easier/a/v2-sat-lesson-circle-theorems",
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:geometry-and-trigonometry-easier/x0fcc98a58ba3bea7:unit-circle-trigonometry-easier/a/v2-sat-lesson-unit-circle-trigonometry",
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:geometry-and-trigonometry-easier/x0fcc98a58ba3bea7:circle-equations-easier/a/v2-sat-lesson-circle-equations",
        ],
    )
    PSD_PCP = (
        "Probability and conditional probability",
        "Math",
        {DifficultyType.EASY: 0.73, DifficultyType.MEDIUM: 0.29, DifficultyType.HARD: 0.07},
        1.10,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:problem-solving-and-data-analysis-easier/x0fcc98a58ba3bea7:probability-and-relative-frequency-easier/a/v2-sat-lesson-probability-and-relative-frequency"
        ],
    )
    PSD_ISS = (
        "Inference from sample statistics and margin of error",
        "Math",
        {DifficultyType.EASY: 0.22, DifficultyType.MEDIUM: 0.37, DifficultyType.HARD: 0.07},
        0.66,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:problem-solving-and-data-analysis-easier/x0fcc98a58ba3bea7:data-inferences-easier/a/v2-sat-lesson-data-inferences"
        ],
    )
    PSD_ESC = (
        "Evaluating statistical claims: Observational studies and experiments",
        "Math",
        {DifficultyType.EASY: 0.00, DifficultyType.MEDIUM: 0.00, DifficultyType.HARD: 0.00},
        0.00,
        [
            "https://www.khanacademy.org/test-prep/v2-sat-math/x0fcc98a58ba3bea7:problem-solving-and-data-analysis-easier/x0fcc98a58ba3bea7:evaluating-statistical-claims-easier/a/v2-sat-lesson-evaluating-statistical-claims"
        ],
    )

    __LABELS__ = {
        "EOI_TRN": "Transitions",
        "EOI_RHS": "Rhetorical Synthesis",
        "CAS_TSP": "Text Structure and Purpose",
        "CAS_WIC": "Words in Context",
        "CAS_XTC": "Cross-text Connections",
        "SEC_BND": "Boundaries",
        "SEC_FSS": "Form, Structure, and Sense",
        "IAI_CID": "Central Ideas and Details",
        "IAI_INF": "Inferences",
        "IAI_COT": "Command of Evidence - Textual",
        "IAI_COQ": "Command of Evidence - Quantitative",
        "ALG_LEO": "Linear equations in one variable",
        "ALG_LIF": "Linear functions",
        "ALG_LET": "Linear equations in two variables",
        "ALG_SLE": "Systems of two linear equations in two variables",
        "ALG_LIN": "Linear inequalities in one or two variables",
        "ADM_NLF": "Nonlinear functions",
        "ADM_NLE": "Nonlinear equations in one variable and systems of equations in two variables",
        "ADM_EQE": "Equivalent expressions",
        "PSD_RRP": "Ratios, rates, proportional relationships, and units",
        "PSD_PER": "Percentages",
        "PSD_OVD": "One-variable data: Distributions and measures of center and spread",
        "PSD_TVD": "Two-variable data: Models and scatterplots",
        "PSD_PCP": "Probability and conditional probability",
        "PSD_ISS": "Inference from sample statistics and margin of error",
        "PSD_ESC": "Evaluating statistical claims: Observational studies and experiments",
        "GAT_AAV": "Area and volume",
        "GAT_LAT": "Lines, angles, and triangles",
        "GAT_RTT": "Right triangles and trigonometry",
        "GAT_CIR": "Circles",
    }

    __CATEGORIES__ = {key: value[1] for key, value in vars().items() if isinstance(value, tuple)}

    @staticmethod
    def get_all_lables():
        return [key.replace("_", "-") for key in SkillType.__LABELS__.keys()]

    @staticmethod
    def get_rw_labels():
        return [key.replace("_", "-") for key, category in SkillType.__CATEGORIES__.items() if category == "RW"]

    @staticmethod
    def get_math_labels():
        return [key.replace("_", "-") for key, category in SkillType.__CATEGORIES__.items() if category == "Math"]

    @staticmethod
    def get_limited_math_labels():
        return [key.replace("_", "-") for key, category in SkillType.__CATEGORIES__.items() if category == "Math"][:15]
if __name__=="__main__":
    rw_skills = [SkillType.__LABELS__[label.replace("-", "_")] for label in SkillType.get_rw_labels()]
    math_skills = [SkillType.__LABELS__[label.replace("-", "_")] for label in SkillType.get_math_labels()]
    print("n.of rw Skills\t: (", len(rw_skills), ")\nrw skills:\n", rw_skills)
    print("n.of rw Skills\t: (", len(math_skills), ")\nrw skills:\n", math_skills)

    skills_json = {
        "skills": {
            "rw": rw_skills,
            "math": math_skills
        }
    }

    print(json.dumps(skills_json, indent=4))