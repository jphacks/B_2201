# TODO: フォーマットに則らない場合のエラー処理

def parse_from_postit(text, insert_newline=False):
    data = []
    title, _, *lines = text.split('\n')
    current_name = ''  # 現在のグループ名
    current_list = []  # 現在のグループのリスト
    temp_data = ''  # 改行がある場合に備え一時的に格納する
    for line in lines:
        if line == '':
            # グループ名リセット
            if temp_data:
                # 一時データがあれば直前のグループ名で保存
                current_list.append(temp_data)
                temp_data = ''
            if current_name:
                data.append({
                    'name': current_name,
                    'list': current_list[:]
                })
                current_name = ''
                current_list = []
        elif current_name == '':
            # グループ名設定
            current_name = line
        elif line.startswith('• ') and temp_data == '':
            # 項目を設定
            temp_data = line[2:]
        elif line.startswith('  '):
            # 項目の文字列に追加
            if insert_newline:
                temp_data += '\n' + line[2:]
            else:
                temp_data += line[2:]
        elif line.startswith('• '):
            # 項目をデータに保存
            current_list.append(temp_data)
            temp_data = line[2:]
    return {'title': title, 'data': data}

demo_text_1 = '''Quick Start
===

Capture
--
• Capture or create Post-it® Notes with this app
• Tap 📷 to capture notes around you
• Tap + to create new notes

Organize
--
• Organize your notes in boards like this
• Tap notes to zoom in
• Tap and hold individual notes to move them
• Drag group to move them
• Tap group names to bring up options
• Tap ⋯ to reveal captured notes

Edit
--
• Edit your notes and their content
• Tap the rotate icon to rotate the note
• Tap the resize icon to resize
• You can resize the notes while editing them
• Tap the note icon to change note color
• Tap keyboard icon to add text
• You can move, scale and rotate text using hand gestures
• You can align the text to the left, center and right
• Tap on the eraser to erase
• Tap on the pens to draw

Share
--
• Share your board with others
• Pick a suitable format
• Tap the share icon to Share
• Use .postit to continue working on another device

'''

demo_text_2 = '''Todo Items
===

Today
--
• Dianne's Birthday
• Groceries

Todo
--
• Shopping
• Farmers Market
• Order New Post-it® Notes
• Holiday
• Pay for Cabin
• Errands
• Pick Up Shirts
• New Collections?

Done
--
• Answer Emails
• Pack Lunch for School
• Bring Extra Clothes

'''

demo_text_3 = '''Oct 15, 2022
===

Group A
--
• 要素だよ

Group C
--

Group B
--
• サンプルのテキスト
  に続くテキストがこんな感じ
  でもちなみに
  この文章は都合が悪かったので
  元の文章から変えてたりします
• テスト2
  改行付き

'''

if __name__ == '__main__':
    import pprint
    pprint.pprint(parse_from_postit(demo_text_1))
    pprint.pprint(parse_from_postit(demo_text_2))
    pprint.pprint(parse_from_postit(demo_text_3))
