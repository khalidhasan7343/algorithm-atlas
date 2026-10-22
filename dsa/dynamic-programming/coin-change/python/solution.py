"""Unbounded minimum coins and unordered combination counts, distinct APIs."""
import json
import sys
import re


def _validate(coins: list[int], amount: int) -> list[int]:
    if type(amount) is not int or not 0 <= amount <= 10000:
        raise ValueError("amount must be an integer in 0..10000")
    if len(coins) > 1000 or len(coins) * (amount + 1) > 2000000:
        raise ValueError("DP work limit exceeded")
    if any(type(c) is not int or not 1 <= c <= 10**9 for c in coins):
        raise ValueError("denominations must be integers in 1..10^9")
    return sorted(set(coins))


def minimum_coins(coins: list[int], amount: int) -> int | None:
    coins = _validate(coins, amount)
    best = [0] + [amount + 1] * amount
    for total in range(1, amount + 1):
        for coin in coins:
            if coin <= total:
                best[total] = min(best[total], best[total - coin] + 1)
    return None if best[amount] > amount else best[amount]


def count_combinations(coins: list[int], amount: int) -> int:
    coins = _validate(coins, amount)
    ways = [1] + [0] * amount
    for coin in coins:
        for total in range(coin, amount + 1):
            ways[total] += ways[total - coin]
            if ways[total] > 2**63 - 1:
                raise OverflowError("combination count table exceeds signed 64-bit")
    return ways[amount]


def _parse(token: str) -> int:
    if not re.fullmatch(r"[+-]?[0-9]+", token):
        raise ValueError("expected ASCII decimal integer")
    return int(token)


if __name__ == "__main__":
    try:
        tokens = [_parse(x) for x in sys.stdin.read().split()]
        if len(tokens) < 2 or not 0 <= tokens[1] <= 1000 or len(tokens) != tokens[1] + 2:
            raise ValueError("expected amount, count, denominations")
        print(json.dumps([minimum_coins(tokens[2:], tokens[0]),
                          count_combinations(tokens[2:], tokens[0])], separators=(",", ":")))
    except (ValueError, OverflowError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
