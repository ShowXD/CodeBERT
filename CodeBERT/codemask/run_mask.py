import os
from typing import Union
from transformers import pipeline, RobertaTokenizer, RobertaForMaskedLM
import pandas as pd
import traceback
from tqdm import tqdm
from multiprocessing import Pool
import re


class CodeMaskDebug:
    """A single mask code prediction task."""

    def __init__(self, tokenizer, model):
        self.tokenizer = tokenizer
        self.model = model
        self.excel_path = ""
        self.sheet_name = ""
        self.clean_error_df = pd.DataFrame

    def load_excel(self, path: str, sheet_name: str, data_cols: list = None):
        """
        讀取 Excel 檔案，並轉換為 DataFrame 格式
        :param path: Excel 檔案路徑
        :param sheet_name: 工作表名稱
        :param data_cols: [原始程式碼欄位名稱, 錯誤訊息欄位名稱]
        :return: DataFrame 格式的 Excel 資料
        """
        if data_cols is None:
            data_cols = ["code", "error_message"]
        try:
            excel_data = pd.read_excel(path, sheet_name=sheet_name, usecols=data_cols)
            excel_data = excel_data.rename(columns={"editorcode": "code", "editorcode_self_testcase_error": "error"})
            excel_data = excel_data[excel_data["error"].notnull()]
            self.clean_error_df = excel_data
        except Exception as e:
            print(f"讀取Excel檔案失敗: {str(e)}")

    def filter_syntax_error_message(self):
        """
        讀取 Dataframe 資料，擷取編譯器錯誤產生的錯誤程式碼
        :return: DataFrame with 錯誤程式碼
        """
        # 讀取 Excel 檔案
        df = self.clean_error_df

        # 轉變成 list
        code_list = df["code"].values.tolist()
        error_message = df["error"].values.tolist()
        title_list = df["title"].values.tolist()
        error_code = []

        # 將沒有"SyntaxError"的字串轉變成空值
        error_code = list(map(lambda x: '' if 'SyntaxError: invalid syntax' not in x else x, error_message))

        # 將含有奇妙字串的欄位轉變成空值
        error_code = list(map(lambda x: '' if '?' in x else x, error_code))  # 為特殊題型
        error_code = list(map(lambda x: '' if 'Traceback (most recent call last):' in x else x, error_code))  # 為輸入錯誤

        # 轉回 Dataframe 格式
        result_df = pd.DataFrame({"code": code_list, "error": error_code, "title": title_list, "error_message": error_message})
        result_df = result_df.loc[result_df["error"] != ""]

        # 重新擷取 error 中的程式碼字串
        code_list = result_df["code"].values.tolist()
        error_code = result_df["error"].values.tolist()
        title_list = result_df["title"].values.tolist()
        error_message = result_df["error_message"].values.tolist()
        error_code = list(map(lambda x: x.split('\n')[1], error_code))

        # 清除頭尾的縮排
        error_code = list(map(lambda x: x.strip(), error_code))

        # 合併回解答
        result_df = pd.DataFrame({"code": code_list, "error": error_code, "title": title_list, "error_message": error_message})

        self.clean_error_df = result_df
        return result_df

    def get_error_line(self):
        """
        讀取 Dataframe 資料，擷取邊義氣判斷的錯誤行數
        :return: DataFrame with 錯誤行數
        """
        # 讀取 Excel 檔案
        df = self.clean_error_df

        # 轉變成 list
        code_list = df["code"].values.tolist()
        error_list = df["error"].values.tolist()
        title_list = df["title"].values.tolist()
        error_message = df["error_message"].values.tolist()
        error_line = []

        # 擷取錯誤行數
        pattern = r"File \"/app/usercode.py\", line (\d+)"
        for row in error_message:
            match = re.search(pattern, row)
            if match:
                line_number = match.group(1)
                error_line.append(int(line_number))
            else:
                error_line.append(0)
                print("No match")

        # 合併回解答
        result_df = pd.DataFrame({"code": code_list, "error": error_list, "title": title_list,
                                  "error_message": error_message, "error_line": error_line})
        self.clean_error_df = result_df
        return result_df

    def check_or_create(self, path):
        """
        判斷路徑是否存在
        :param path: 路徑
        :output: 路徑不存在則建立
        """
        dir_path = os.path.dirname(path)

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

    def to_excel(self, data: Union[list, pd.DataFrame], path):
        """
        資料寫入 Excel 檔案
        :param data: 要寫入的資料
        :param path: 要寫入的路徑
        :output: Excel檔案
        :return: None
        """
        if isinstance(data, list):
            data = pd.DataFrame(data)
            self.to_excel(data, path)
        elif isinstance(data, pd.DataFrame):
            self.check_or_create(path)
            data.to_excel(path, index=False)
            # data.to_excel(f"{path}/clear_error_code.xlsx", index=False)
            print("寫入 Excel 檔案成功")
        else:
            print("輸入型態不支援")

    def add_mask_to_code(self, code, tokenizer, mask_token="<mask>"):
        """
        將輸入的程式碼可以合理填入 mask 的位置加入 mask token
        :param code: 程式碼
        :param tokenizer: 分詞器
        :param mask_token: 要加入的字符
        :return: 加入 mask token 的程式碼
        """
        # 使用微軟的分詞器
        result_code_list = []
        code_token_list = tokenizer.tokenize(code)
        code_token_list = [x.replace('\u0120', '') for x in code_token_list]
        # 分符出來的個別 mask
        for index, code_token in enumerate(code_token_list):
            tmp = code_token_list.copy()
            code_token_list[index] = mask_token
            result_code_list.append(code_token_list)
            code_token_list = tmp
        # 頭加入 mask
        tmp = code_token_list.copy()
        code_token_list.insert(0, mask_token)
        result_code_list.append(code_token_list)
        code_token_list = tmp
        # 間隔裡加入mask
        for i in range(len(code_token_list)):
            tmp = code_token_list.copy()
            code_token_list.insert(i + 1, mask_token)
            result_code_list.append(code_token_list)
            code_token_list = tmp

        return result_code_list

    def combine_mask_code_to_code(self, error_code, mask_code, code):
        """
        將 mask token 的程式碼與原始程式碼合併
        :param error_code: error 訊息的程式碼
        :param mask_code: 經過 mask 的程式碼
        :param code: 原始程式碼
        :return: mask 過後的完整程式碼
        """
        mask_code_str = " ".join(mask_code)
        masked_full_code = code.replace(error_code, mask_code_str)

        return masked_full_code

    def model_guess(self, index, row):
        """
        使用 model 預測程式碼
        .param index: 第幾題
        :param row: 第幾題的程式碼
        :return: model 預測的程式碼列表
        """
        guess_code_list = []
        df = self.clean_error_df
        # 載入模型
        fill_mask = pipeline('fill-mask', model=self.model, tokenizer=self.tokenizer)
        # 將程式碼加入 mask

        # for i, row in df.iterrows():
        mask_message_code_list = self.add_mask_to_code(df['error'][index], self.tokenizer)
        for mask_message_code in mask_message_code_list:
            full_code = self.combine_mask_code_to_code(df['error'][index], mask_message_code, df['code'][index])
            outputs = fill_mask(full_code)
            guess_code_list.append(outputs[0])  # 取機率最大的一個


        return guess_code_list

    def multi_model_guess(self):
        """
        由於一題可以多個能夠 mask 的地方，因此在這裡一筆一筆傳給 model_guess，使其能夠回傳單一 list
        """
        df = self.clean_error_df
        for index, row in df.iterrows():
            guess_list = self.model_guess(index, row)
            self.generate_guess_code_to_py(index, guess_list)

        self.to_excel(df, os.path.join("generated_code", "all_data.xlsx"))

    def remove_special_token(self, code):
        """
        移除預測出來的程式碼中的特殊符號
        :param code: 預測出來的程式碼
        :return: 移除特殊符號後的程式碼
        """
        code = code.replace('<s>', '').replace('</s>', '')
        return code

    def generate_guess_code_to_py(self, topic, data):
        """
        將 CodeBERT 猜的程式碼寫入檔案
        :param topic: 第幾題
        :param data: CodeBERT 猜的程式碼 list
        """
        print(f"開始寫入第{topic+1}題檔案")
        path = os.path.join("generated_code", str(topic))
        if isinstance(data, list):  # 多個預測結果
            for index, code in enumerate(data):
                file_path = os.path.join(path, f"python_{index + 1}.py")
                self.check_or_create(file_path)
                code = self.remove_special_token(code['sequence'])
                try:
                    with open(file_path, "w", encoding='utf-8') as f:
                        f.write(code)
                    print(f"第{topic+1}個檔案寫入成功")
                except Exception as e:
                    print(e)
        elif isinstance(data, dict):  # 單個預測結果
            file_path = os.path.join(path, "codebert_guess.py")
            self.check_or_create(file_path)
            code = self.remove_special_token(data['sequence'])
            try:
                with open(file_path, "w", encoding='utf-8') as f:
                    f.write(code)
            except Exception as e:
                print("單 dict 寫入失敗")
        else:
            print("輸入型態不支援")
        export_path = os.path.join(path, f"{topic}.xlsx")
        print(export_path)
        self.to_excel(data, export_path)

    def get_error_position(self, error_message):
        """
        取得錯誤訊息的位置
        :param error_message: 錯誤訊息
        :return: 錯誤訊息的位置
        """
        error_list = self.clean_error_df["error"].values.tolist()

        for index, error in enumerate(error_list):
            print(traceback.print_tb(error))

        return 0

    def error_excel_generate_model_results(self, excel_path: str, excel_sheet_name: str, column_name: list):
        self.load_excel(excel_path, excel_sheet_name, column_name)
        self.filter_syntax_error_message()
        self.get_error_line()
        self.clean_error_df = self.clean_error_df.head(10)
        print(self.clean_error_df)
        # guess_list = self.model_guess(self.clean_error_df)
        # self.to_excel(guess_list)
        # self.multi_model_guess()


def main():
    code_mask_debug = CodeMaskDebug(
        tokenizer=RobertaTokenizer.from_pretrained("microsoft/codebert-base-mlm"),
        model=RobertaForMaskedLM.from_pretrained("microsoft/codebert-base-mlm"),
    )
    excel_path = "../../data/codemask/pytutor/pytutor_usercode_backend_2023-02-06_11_58_45.xlsx"
    sheet_name = "Sheet1"
    code_mask_debug.load_excel(excel_path, sheet_name, ["editorcode", "editorcode_self_testcase_error", "title"])
    code_mask_debug.error_excel_generate_model_results(excel_path, sheet_name,
                                                 ["editorcode", "editorcode_self_testcase_error", "title"])


if __name__ == "__main__":
    main()
