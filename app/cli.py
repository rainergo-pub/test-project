import sys

from app.stock import diff_counts, load_counts


def main():
    a = load_counts(sys.argv[1])
    b = load_counts(sys.argv[2])
    for sku, delta in diff_counts(a, b).items():
        print(sku, delta)


if __name__ == "__main__":
    main()
