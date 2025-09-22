import lmstudio as lms

# dir()関数を使って、ライブラリに含まれるすべての要素を表示
# print(dir(lms))

for ls in dir(lms):
    if ls == "embedding_model":
        print("Found embedding_model in lmstudio")
    else:
        pass