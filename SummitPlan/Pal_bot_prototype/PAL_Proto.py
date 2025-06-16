from template import gen_pal_output
from user_data_test import get_data

if __name__ == "__main__":
    user = "Aarthi"
    data = get_data(user)
    print(gen_pal_output(data))