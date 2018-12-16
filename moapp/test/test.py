def ui(): # 定义一个函数
    # 声明MoApp（注，一个小程序只能有一个MoApp）
    with MoApp(appid='wx4ecd2c3018e1dd6b', name='MoApp Demo'):
        # 定义一个小程序页面
        with Page(name='first'):
            Input(name='input1', placeholder='请输入你的名字', pos=['center', 180], size=[700, 70], border='1px solid #ccc')
            Button(text='撩一撩', pos=['center', 500], width=700, onTap=helloMoApp)


async def helloMoApp(user, app, page, mo):
    mo.showTips('你好啊,' + page.input1.value)