
EXPECTED_FIELDS: list[str] = ['class_name', 'distance', 'top_left_x','top_left_y','top_right_x','top_right_y','bottom_left_x','bottom_left_y','bottom_right_x','bottom_right_y']
GREEN: str
YELLOW: str
RED: str
RESET: str
GREEN, YELLOW, RED, RESET = "\033[32m", "\033[33m", "\033[31m", "\033[0m"
TOLERANCE: int = 5 #Pixels
ABBREVIATIONS: dict[str, str] = {
    'top_left_x': 'tl_x', 'top_left_y': 'tl_y',
    'top_right_x': 'tr_x', 'top_right_y': 'tr_y',
    'bottom_left_x': 'bl_x', 'bottom_left_y': 'bl_y',
    'bottom_right_x': 'br_x', 'bottom_right_y': 'br_y',
    'class_name': 'cls'
}


class Comparator:

    def __init__(self, expected: list[dict[str, str]], result: list[dict[str, str]]) -> None:
        self.expected: list[dict[str, str]] = expected
        self.result: list[dict[str, str]] = result


    def __format_result(self, d: dict[str, str]) -> str:
        return ", ".join(f"{ABBREVIATIONS.get(k, k)}={d.get(k)}" for k in EXPECTED_FIELDS)


    def __is_match(self, exp: dict[str, str], got: dict[str, str]) -> bool:
        if exp['class_name'] != got.get('class_name'):
            return False
        for field in EXPECTED_FIELDS[2:]:
            expected_value: float
            got_value: float
            expected_value, got_value = float(exp[field]), float(got[field])
            if abs(got_value - expected_value) > TOLERANCE:
                return False
        return True


    def compare(self) -> None:
        success: int = 0
        unmatched: list[dict[str, str]] = list(self.result)
        for exp in self.expected:
            got: dict[str, str] | None = next((r for r in unmatched if self.__is_match(exp, r)), None)
            if got:
                unmatched.remove(got)
                success += 1
                print(f"{GREEN}[MATCHED]{RESET} {self.__format_result(got)}")
            else:
                print(f"{RED}[MISSING]{RESET} {self.__format_result(exp)}")
        for r in unmatched:
            print(f"{RED}[EXTRA]{RESET} {self.__format_result(r)}")
        success_rate: float = success*100/len(self.expected)
        success_color: str
        match success_rate:
            case rate if rate > 90:
                success_color = GREEN
            case rate if rate > 60:
                success_color = YELLOW
            case _:
                success_color = RED
        print(f"==={success_color} {success*100/len(self.expected):.2f}% ({success}/{len(self.expected)}){RESET} ===\n")