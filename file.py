# matrix_string_toolkit.py
# Core algorithms implemented from first principles.
# Allowed: basic Python built-ins (no numpy, no regex, no collections helpers).

from typing import List, Tuple, Optional

Number = float  # keep it simple; could be Fraction for exactness

# -------------------------
# Matrix utilities
# -------------------------

def zeros(n: int, m: int) -> List[List[Number]]:
    return [[0.0 for _ in range(m)] for _ in range(n)]

def identity(n: int) -> List[List[Number]]:
    I = zeros(n, n)
    for i in range(n): I[i][i] = 1.0
    return I

def shape(A: List[List[Number]]) -> Tuple[int, int]:
    return (len(A), len(A[0]) if A else 0)

def copy_matrix(A: List[List[Number]]) -> List[List[Number]]:
    return [row[:] for row in A]

def mat_add(A: List[List[Number]], B: List[List[Number]]) -> List[List[Number]]:
    n, m = shape(A)
    nb, mb = shape(B)
    if (n, m) != (nb, mb): raise ValueError("add: shape mismatch")
    C = zeros(n, m)
    for i in range(n):
        for j in range(m):
            C[i][j] = A[i][j] + B[i][j]
    return C

def mat_sub(A: List[List[Number]], B: List[List[Number]]) -> List[List[Number]]:
    n, m = shape(A)
    nb, mb = shape(B)
    if (n, m) != (nb, mb): raise ValueError("sub: shape mismatch")
    C = zeros(n, m)
    for i in range(n):
        for j in range(m):
            C[i][j] = A[i][j] - B[i][j]
    return C

def mat_mul(A: List[List[Number]], B: List[List[Number]]) -> List[List[Number]]:
    n, m = shape(A)
    p, q = shape(B)
    if m != p: raise ValueError("mul: inner dims mismatch")
    C = zeros(n, q)
    for i in range(n):
        for k in range(m):
            aik = A[i][k]
            for j in range(q):
                C[i][j] += aik * B[k][j]
    return C

def transpose(A: List[List[Number]]) -> List[List[Number]]:
    n, m = shape(A)
    T = zeros(m, n)
    for i in range(n):
        for j in range(m):
            T[j][i] = A[i][j]
    return T

def lu_decompose(A: List[List[Number]], eps: float = 1e-12) -> Tuple[List[List[Number]], List[List[Number]], List[int], int]:
    # Doolittle with partial pivoting: PA = LU
    n, m = shape(A)
    if n != m: raise ValueError("LU: square matrix required")
    U = copy_matrix(A)
    L = identity(n)
    P = list(range(n))
    swaps = 0
    for k in range(n):
        # pivot
        piv = k
        maxabs = abs(U[k][k])
        for r in range(k+1, n):
            v = abs(U[r][k])
            if v > maxabs:
                maxabs = v; piv = r
        if maxabs < eps: raise ValueError("LU: singular matrix")
        if piv != k:
            U[k], U[piv] = U[piv], U[k]
            L[k][:k], L[piv][:k] = L[piv][:k], L[k][:k]
            P[k], P[piv] = P[piv], P[k]
            swaps += 1
        # elimination
        for i in range(k+1, n):
            L[i][k] = U[i][k] / U[k][k]
            factor = L[i][k]
            for j in range(k, n):
                U[i][j] -= factor * U[k][j]
    return L, U, P, swaps

def det(A: List[List[Number]]) -> Number:
    L, U, _, swaps = lu_decompose(A)
    d = 1.0
    for i in range(len(U)):
        d *= U[i][i]
    return -d if (swaps % 2) else d

def solve_lu(L: List[List[Number]], U: List[List[Number]], P: List[int], b: List[Number]) -> List[Number]:
    n = len(L)
    # Apply permutation Pb
    bp = [b[P[i]] for i in range(n)]
    # forward solve Ly=Pb
    y = [0.0]*n
    for i in range(n):
        s = bp[i]
        for j in range(i):
            s -= L[i][j]*y[j]
        y[i] = s  # L has 1s on diagonal
    # backward solve Ux=y
    x = [0.0]*n
    for i in range(n-1, -1, -1):
        s = y[i]
        for j in range(i+1, n):
            s -= U[i][j]*x[j]
        if abs(U[i][i]) < 1e-12: raise ValueError("solve: singular")
        x[i] = s / U[i][i]
    return x

def inverse(A: List[List[Number]]) -> List[List[Number]]:
    n, m = shape(A)
    if n != m: raise ValueError("inv: square required")
    L, U, P, _ = lu_decompose(A)
    invA = zeros(n, n)
    for col in range(n):
        e = [0.0]*n
        e[col] = 1.0
        x = solve_lu(L, U, P, e)
        for i in range(n):
            invA[i][col] = x[i]
    return invA

# -------------------------
# Advanced string logic
# -------------------------

def to_lower(s: str) -> str:
    # manual ascii lower
    out = []
    for ch in s:
        o = ord(ch)
        if 65 <= o <= 90:
            out.append(chr(o + 32))
        else:
            out.append(ch)
    return "".join(out)

def trim(s: str) -> str:
    # trim spaces, tabs, newlines
    i, j = 0, len(s) - 1
    while i <= j and s[i] in " \t\n\r":
        i += 1
    while j >= i and s[j] in " \t\n\r":
        j -= 1
    return s[i:j+1]

def split_simple(s: str, sep: str) -> List[str]:
    # single-char separator, no regex
    parts = []
    cur = []
    for ch in s:
        if ch == sep:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return parts

def reverse_words(s: str) -> str:
    # reverse characters of each word; preserve single spaces
    res = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] == ' ':
            res.append(' ')
            i += 1
        else:
            j = i
            while j < n and s[j] != ' ':
                j += 1
            # reverse [i:j]
            k = j - 1
            while k >= i:
                res.append(s[k])
                k -= 1
            i = j
    return "".join(res)

def is_palindrome(s: str) -> bool:
    # alnum-only, case-insensitive, two-pointer
    i, j = 0, len(s) - 1
    while i < j:
        ci, cj = s[i], s[j]
        # advance to alnum
        if not (('0' <= ci <= '9') or ('A' <= ci <= 'Z') or ('a' <= ci <= 'z')):
            i += 1; continue
        if not (('0' <= cj <= '9') or ('A' <= cj <= 'Z') or ('a' <= cj <= 'z')):
            j -= 1; continue
        oi, oj = ord(ci), ord(cj)
        if 65 <= oi <= 90: oi += 32
        if 65 <= oj <= 90: oj += 32
        if oi != oj: return False
        i += 1; j -= 1
    return True

def longest_common_subsequence(a: str, b: str) -> str:
    # DP, O(nm) space/time, build string without libs
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    for i in range(n-1, -1, -1):
        for j in range(m-1, -1, -1):
            if a[i] == b[j]:
                dp[i][j] = 1 + dp[i+1][j+1]
            else:
                dp[i][j] = dp[i+1][j] if dp[i+1][j] >= dp[i][j+1] else dp[i][j+1]
    # reconstruct
    i = j = 0
    out = []
    while i < n and j < m:
        if a[i] == b[j]:
            out.append(a[i]); i += 1; j += 1
        elif dp[i+1][j] >= dp[i][j+1]:
            i += 1
        else:
            j += 1
    return "".join(out)

# -------------------------
# Self-tests (basic)
# -------------------------

def _almost_equal(a: float, b: float, tol: float = 1e-9) -> bool:
    d = a - b
    if d < 0: d = -d
    return d <= tol

def run_tests() -> None:
    # Matrix tests
    A = [[4.0, 7.0], [2.0, 6.0]]
    B = [[3.0, 8.0], [5.0, 1.0]]
    assert mat_add(A, B) == [[7.0, 15.0],[7.0, 7.0]]
    assert mat_sub(A, B) == [[1.0, -1.0],[-3.0, 5.0]]
    C = mat_mul(A, B)
    assert C == [[4*3+7*5, 4*8+7*1],[2*3+6*5, 2*8+6*1]]
    d = det(A)
    assert _almost_equal(d, 4*6 - 7*2)
    invA = inverse(A)
    should_be_I = mat_mul(A, invA)
    for i in range(2):
        for j in range(2):
            if i == j:
                assert _almost_equal(should_be_I[i][j], 1.0, 1e-7)
            else:
                assert _almost_equal(should_be_I[i][j], 0.0, 1e-7)

    # String tests
    assert to_lower("HeLLo!") == "hello!"
    assert trim("  hi \n") == "hi"
    assert split_simple("a,b,,c", ",") == ["a", "b", "", "c"]
    assert reverse_words("abc def") == "cba fed"
    assert is_palindrome("A man, a plan, a canal: Panama") is True
    assert longest_common_subsequence("ABCBDAB", "BDCABA") == "BCBA"

if __name__ == "__main__":
    run_tests()
    print("All tests passed.")
