def levenshtein(s1, s2):
    s1 = s1.upper()
    s2 = s2.upper()
    dp = [[0 for _ in range(len(s2))] for _ in range(len(s1))]
    for i in range(len(s1)):
        for j in range(len(s2)):
            if i == 0 and j == 0:
                if s1[i] == s2[j]:
                    dp[0][0] = 0
                else:
                    dp[0][0] = 1
            elif i == 0:
                if s1[i] == s2[j]:
                    dp[0][j] = j
                else:
                    dp[0][j] = j + 1
            elif j == 0:
                if s1[i] == s2[j]:
                    dp[i][0] = i
                else:
                    dp[i][0] = i + 1
            else:
                if s1[i] == s2[j]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    modify = dp[i - 1][j - 1] + 1
                    del_s1 = dp[i - 1][j] + 1
                    del_s2 = dp[i][j - 1] + 1
                    dp[i][j] = min(modify, del_s1, del_s2)
    return dp[len(s1) - 1][len(s2) - 1]
