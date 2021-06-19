import math


class StaticUtilities:
    @staticmethod
    def get_factors_as_pairs(num):
        factor_list = []
        end = math.floor(math.sqrt(num))
        for i in range(end):
            i += 1
            if num % i == 0:
                a = int(i)
                b = int(num / i)
                factor_list.append([a, b])

        reverse_factor_list = []
        list_len = len(factor_list)

        # Reverse the list to get all the ordered pairs
        for i in range(list_len):
            j = list_len - i - 1
            val = factor_list[j]
            new_val = [val[1], val[0]]
            if not val[0] == val[1]:
                reverse_factor_list.append(new_val)

        factor_list += reverse_factor_list
        return factor_list
