import json
import time
import asyncio
from llama_cloud_services import LlamaParse
from dotenv import load_dotenv

load_dotenv()

# formats = ["NO", "品名", "型番", "数量", "同等品可否", "調達要求番号", "物品番号", "納地", "引渡場所", "搬入場所", "納期"] # 102n
# formats = ["番号", "品名", "規格", "単位", "数量"] # 239n
# formats = ["NO", "品名", "規格", "単位", "数量"] # 471n
# formats = ["商品名", "数量", "単位", "単価", "金額"] # img-01
# formats = ["商品名", "注文番号", "数量","単価", "金額"] # img-03
formats = ["商品名", "数量", "単価", "金額"] # img-01, 03

async def main():
	prompt = f"""
あなたはPDFから表データを抽出するAIアシスタントです。  
PDF内の「正式な注文表」に含まれるすべての行を抽出してください。  
【抽出対象】  
1. 「注文番号」「数量」「単価」「金額」が揃っている正式な注文表の行をすべて抽出する。  
2. 注文表の途中で改行やセル結合があっても、必ず1行として結合して抽出する。  
3. 表かどうか曖昧な場合でも、正式な注文表のパターンに合致する行はすべて抽出する。  
4. 付属品・参考情報・明らかに注文表ではない行以外は除外しない。  
5. すべての正式な注文表の行を漏れなく抽出すること。  
6. 欠落や見逃しがないように、行が少しでも表の形式を満たす場合は必ず抽出する。
【抽出ルール】  
1. 各行を1つのオブジェクトとして抽出する。  
2. 数量は単位（台・枚など）を除去して数値のみ抽出する。  
3. 注文番号は英字・数字・-・/ の組み合わせとする。  
4. 「同等」という文字が含まれる場合、"同等品可否": "同等品" を追加する。  
5. 型番は英数字・-・/ のみを抽出し、日本語部分は品名に含める。  
6. すべての正式な注文表の行を可能な限り抽出し、絶対に漏れがないようにする。  
7. 抽出対象行は少しでも注文表の特徴があれば必ず含める。  
【データ形式】  
1. 数値（数量・単価・金額）は文字列として返す。必要に応じてカンマ区切りを使用できる。  
    - 例: 11100 → "11,100"、50 → "50"  
【出力形式】  
1. 出力は必ず有効なJSON配列のみとする。  
2. JSON配列は必ず `[` で始まり `]` で終わり、その外側には一切文字を出さないこと。  
3. JSON配列は1つだけ出力し、その中にすべての表データをまとめること。  
4. JSON配列以外（文章・表記法・マークダウン・空行など）を含めないこと。  
5. JSON配列以外を絶対に含めない。  
6. JSON配列は必ず1つにまとめ、途中で分割したり複数個にしないこと。  
【出力例】  
出力は必ず以下の形式の JSON 配列とする：
```
[
		{{"\n{",\n".join([f'        "{item}": "〇〇〇"' for item in formats])}\n    }},
		...
]  
```
"""


	start_time = time.time()
	result = await LlamaParse(
		parse_mode="parse_page_with_agent",
		target_pages="0, 3, 2, 15",
		model="openai-gpt-4-1-mini",
		high_res_ocr=True,
		adaptive_long_table=True,
		result_type="markdown",
		language="ja",
		user_prompt=prompt,
	).aparse("img-01.pdf")

	documents = result.get_markdown_documents(split_by_page=True)

	parsed_time = time.time()
	print(f"Parsed time: {parsed_time - start_time:.2f} seconds")

	try:
		with open("parseC.json", "w", encoding="utf-8") as f:
			text = "".join(doc.text for doc in documents)
			print(text, file=f)
	except Exception as e:
		print(f"Error writing text.json: {e}")

	# processed_answers = []
	# for i, doc in enumerate(result):
	# 	text = doc.text.strip()
	# 	if text.startswith("[") and text.endswith("]"):
	# 		try:
	# 			answer = json.loads(text)
	# 			if len(answer) > 0:
	# 				processed_answers.extend(answer)
	# 		except json.JSONDecodeError as e:
	# 			print(f"JSON decode error on page {i}: {e}")
	# 		except Exception as e:
	# 			print(f"Unexpected error parsing JSON on page {i}: {e}")

	# try:
	# 	with open("parseC.json", "w", encoding="utf-8") as f:
	# 		json.dump(processed_answers, f, ensure_ascii=False, indent=2)
	# except Exception as e:
	# 	print(f"Error writing parseC.json: {e}")

if __name__ == "__main__":
    asyncio.run(main())