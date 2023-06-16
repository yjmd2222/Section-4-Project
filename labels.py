'''
classifier output labels
'''
classes = {0: '거북목', 1: '등기댐', 2: '정상'}
classes_eng = {v: eng_v for v, eng_v in zip(classes.values(), ['forward_head', 'leaning', 'normal'])}
