import sys
import json


def karsilastir(dosya1: str, dosya2: str) -> bool:
    try:
        with open(dosya1, "r", encoding="utf-8") as f1, open(dosya2, "r", encoding="utf-8") as f2:
            satirlar1 = [s.strip() for s in f1 if s.strip()]
            satirlar2 = [s.strip() for s in f2 if s.strip()]

        if len(satirlar1) != len(satirlar2):
            return False

        for s1, s2 in zip(satirlar1, satirlar2):
            try:
                if json.loads(s1) != json.loads(s2):
                    return False
            except json.JSONDecodeError:
                if s1 != s2:
                    return False

        return True
    except Exception:
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Kullanım: python karsilastir.py <dosya1> <dosya2>")
        sys.exit(2)

    esit = karsilastir(sys.argv[1], sys.argv[2])
    print(esit)
    sys.exit(0 if esit else 1)
