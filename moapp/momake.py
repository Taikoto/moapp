'''
    depends:
        zip
'''
#coding=utf-8
import requests
import json
import sys
import os
import re
import zipfile
import time
import uuid
import tempfile
import traceback
import threading
from tkinter import *
import tkinter.font as tkFont
from tkinter.filedialog import askdirectory
from tkinter.scrolledtext import ScrolledText

momake_server = {
    'dev': 'http://dev.xiakego.cn/momake/v1',
    'test': 'http://momake.moapp.mogotea.cn/v1',
    'release': 'http://momake.moapp.mogotea.cn/v1'
}

def make_dir_s(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def zipFolder(path, fileName, skipFolders, skipExts, log):
    '''
        path: 待打包的文件夹，如:D:/MOGO/codes/moapp/samples/hust_borrow
        fileName: 输出zip文件路径，如:D:/MOGO/codes/moapp/samples/test.zip
        skipFolders：不用打包的文件夹列表，如: ['__pycache__']
        skipExts: 不用打包的文件扩展名列表，如：['.exe', '.zip']
    '''
    fileList = []
    newZip = zipfile.ZipFile(fileName,'w')
    for dirpath,dirnames,filenames in os.walk(path):
        for filename in filenames:
            filePath = os.path.join(dirpath,filename).replace('\\', '/')
            skip = False
            for skipFolder in skipFolders:
                if filePath.find(('%s/%s' %(path, skipFolder)).replace('\\', '/')) > -1:
                    skip = True
                    break

            # 检查是否过滤扩展名
            if not skip:
                for ext in skipExts:
                    pos = 0 - len(ext)
                    if filePath[pos:].lower() == ext.lower():
                        skip = True
                        break

            if not skip:
                log('\tpack file:%s' %filePath)
                fileList.append(filePath)
            else:
                log('\tskip file:%s' %filePath)
    
    for tar in fileList:
        newZip.write(tar,tar[len(path):])#, compress_type=zipfile.ZIP_LZMA)
    newZip.close()

def make(root_path, out_path, env, log):
    '''
        生成moapp
        root_path: 代码根路径
        out_path: 小程序代码输出路径
        env: 环境: dev|test|release
    '''    
    file_items = {}
    log('--------------prepare to make--------------')
    tmp_src_zip = 'src_%s.zip' %int(time.time())
    log('begin pack source folder...')
    zipFolder(root_path, tmp_src_zip, ['__pycache__', '.DS_Store'], ['.exe', '.zip', '.bak', '.pyc'], log)
    zipSize = os.path.getsize(tmp_src_zip)
    log('\tend pack source folder, size: %.2f KB' %(zipSize/1024.0))

    if zipSize > 1024*1024:
        log('[ Error ]source folder is greater than 1 MB! please remove unnesessary files!')
        return
    try:
        log('begin request to momake...%s' %momake_server[env])
        res = None

        with open(tmp_src_zip,'rb') as srcZip:
            files = {'codes': srcZip}
            res = requests.post(momake_server[env], data = {
                'root_path': root_path,
                'env': env
                }, files=files, timeout=30)

        log('\tend request')
        if res and res.status_code == 200:
            if isinstance(res.text, bytes):
                res.text = res.text.decode(errors='replace')

            res = json.loads(res.text)
            if 'ret' in res and res['ret'] == 0:
                log('begin download zip...')
                log('\turl:%s' %(res['data']['url']))
                file_url = res['data']['url']
                if momake_server[env].find('https://') > -1:
                    file_url = file_url.replace('http://', 'https://')

                r = requests.get(file_url, stream= True, verify=False)
                tmp_file = '%s.zip' %(int(time.time()))
                with open(tmp_file, 'wb') as f:
                    f.write(r.content)
                log('begin unzip...')
                make_dir_s(out_path)
                with zipfile.ZipFile(tmp_file, 'r') as z:
                    for f in z.namelist():
                        pos = f.rfind('/')
                        if pos > -1:
                            path = '%s/%s' %(out_path, f[0:pos])
                            make_dir_s(path)

                        if f.find('.') > -1:
                            log('\tsave file:%s' %f)
                            with open('%s/%s' %(out_path, f), 'wb') as o:
                                o.write(z.read(f))

                try:
                    os.remove(tmp_file)
                except:
                    pass

                log('--------------make moapp successed--------------')
            else:
                log('momake fail !!! error message:\n---------------------------------------------')
                if 'data' in res and 'stderr' in res['data']:
                    log(res['data']['stderr'])
                else:
                    log(json.dumps(res))
        else:
            log('momake server err:\n%s' %res.text)
    except Exception as ex:
        log('momake exceptions, err:\n%s' %(str(ex)))
        log('callack:\n%s' %(traceback.format_exc()))

    try:
        os.remove(tmp_src_zip)        
    except Exception as ex:
        log('momake exceptions, err:\n%s' %(str(ex)))
        log('callack:\n%s' %(traceback.format_exc()))

class TaskThread(threading.Thread):
    def __init__(self, root_path, out_path, env, log, onFinish):
        threading.Thread.__init__(self)
        self.rootPath = root_path
        self.outPath = out_path
        self.env = env
        self.log = log
        self.onFinish = onFinish

    def run(self):
        make(self.rootPath, self.outPath, self.env, self.log)
        self.onFinish()

def help():
    print('Usage:')
    print('\tpython momake.py src={SRC_PATH} dst={DES_PATH} env={ENV}')
    print('\t\tSRC_PATH: the source path')
    print('\t\tDST_PATH: the output path')
    print('\t\tENV: the enviriment of the target, dev|test|release')
    print('Example:')
    print('python momake.py src=d:/mogo/myapp dst=d:/moapp/myapp env=test')

# 配置文件读写
class Config():
    def __init__(self, file_path):
        self.__path = file_path
        self.__value = {}

        try:
            with open(self.__path, 'r+', encoding='utf-8') as f:
                content = f.read()
                if isinstance(content, bytes):
                    content = content.decode()
                self.__value = json.loads(content)
        except:
            pass

    def get(self, k):
        if k in self.__value:
            return self.__value[k]
        else:
            return ''

    def set(self, k, v):
        self.__value[k] = v
        self._save()

    def _save(self):
        with open(self.__path, 'w+', encoding='utf-8') as f:
            f.write(json.dumps(self.__value, indent=4))


class MoMakeApp(Frame):
    def __init__(self, master=None):        
        Frame.__init__(self, master)
        self.pack()

        cfg_file = '%s/momake.cfg.json' %(tempfile.gettempdir())
        self.cfg = Config(cfg_file)

        self.master.title('MoMake v0.3')
        self.master.geometry('740x480')
        self.master.resizable(0, 0)
        
        self.src_path = StringVar()
        self.src_path.set(self.cfg.get('src'))
        self.dst_path = StringVar()
        self.dst_path.set(self.cfg.get('dst'))
        self.env = StringVar()
        self.env.set(self.cfg.get('env') or 'test')

        ft = tkFont.Font(family='微软雅黑', size=12)
        row_span = 20
        Label(self, text="代码路径: ", font=ft).grid(row=0, sticky=E, pady=row_span)
        e = Entry(self, font=ft, width=60, textvariable=self.src_path)
        e.grid(row=0,column=1,sticky=W, columnspan=4)
        e.bind('<KeyPress>', lambda e:'break') # 禁止输入
        self.chooseSrcPath = Button(self,text="选择...", font=ft, command=self.__chooseSrcPath)
        self.chooseSrcPath.grid(row=0,column=5,sticky=E, padx=15)
        
        Label(self,text = "输出路径: ", font=ft).grid(row=1,sticky=E)
        e = Entry(self, font=ft, width=60, textvariable=self.dst_path)
        e.grid(row=1,column=1,sticky=W, columnspan=4)
        e.bind('<KeyPress>', lambda e:'break')  # 禁止输入
        self.chooseDistPath = Button(self,text="选择...", height=1, font=ft, command=self.__chooseDstPath)
        self.chooseDistPath.grid(row=1,column=5,sticky=E, padx=15)

        Label(self,text = "环境: ", font=ft).grid(row=2,sticky=E)
        #Radiobutton(self, text='开发环境', value='dev', variable=self.env, font=ft).grid(row=2, sticky=W, column=1)
        self.radioEnvTest = Radiobutton(self, text='测试环境', value='test', variable=self.env, font=ft)
        self.radioEnvTest.grid(row=2, sticky=W, column=1)
        self.radioEnvRelease = Radiobutton(self, text='正式环境', value='release', variable=self.env, font=ft)
        self.radioEnvRelease.grid(row=2, sticky=W, column=2)

        self.create = Button(self,text="生成小程序", font=ft, width=20, height=1, command=self.__create)
        self.create.grid(row=3,column=0, columnspan=6, pady=row_span)
        self.create['state'] = DISABLED
        
        self.output = ScrolledText(self, borderwidth=1, width=98, height=19)
        self.output.bind('<KeyPress>', lambda e:'break') # 禁止输入
        self.output.grid(row=4, column=0, columnspan=6)

        self.__refreshState()

    def __chooseSrcPath(self):
        path = askdirectory(initialdir=self.src_path.get(), title='请选择python代码文件夹')
        if path:
            self.src_path.set(path)
            self.__output('choose src path:%s' %path)
            self.__refreshState()

    def __chooseDstPath(self):
        path = askdirectory(initialdir=self.dst_path.get(), title='请选择小程序输出文件夹')
        if path:
            self.dst_path.set(path)
            self.__output('choose dst path:%s' %path)
            self.__refreshState()

    def __refreshState(self):
        if os.path.isdir(self.src_path.get()) and os.path.isdir(self.dst_path.get()):
            self.create['state'] = NORMAL
        else:
            self.create['state'] = DISABLED

    def __output(self, text):        
        if text[0:1] != '\t':
            if text != '':
                text = '%s %s' %(time.strftime("%H:%M:%S", time.localtime()), text)
        else:
            text = text.replace('\t', '         ')

        self.output.insert(END, text)
        self.output.insert(END, '\n')
        self.output.see(END)

    def onFinish(self):
        self.__output('')
        self.create['state'] = NORMAL
        self.create['text'] = '生成小程序'

        self.chooseSrcPath['state'] = NORMAL
        self.chooseDistPath['state'] = NORMAL
        self.radioEnvTest['state'] = NORMAL
        self.radioEnvRelease['state'] = NORMAL

    def __create(self):
        self.output.delete(1.0, END)
        self.cfg.set('src', self.src_path.get())
        self.cfg.set('dst', self.dst_path.get())
        self.cfg.set('env', self.env.get())

        self.create['state'] = DISABLED
        self.chooseSrcPath['state'] = DISABLED
        self.chooseDistPath['state'] = DISABLED
        self.radioEnvTest['state'] = DISABLED
        self.radioEnvRelease['state'] = DISABLED

        self.create['text'] = '制作中，请稍后...'
        t = TaskThread(self.src_path.get(), self.dst_path.get(), self.env.get(), self.__output, self.onFinish)
        t.start()
        

# gui模式
def run_gui():
    MoMakeApp().mainloop()

# 命令行模式
def run_console():
    if len(sys.argv) == 4:
        src = ''
        dst = ''
        env = ''

        for i in range(1, len(sys.argv)):
            item = sys.argv[i].split('=')
            if len(item) == 2:
                k = item[0].strip()
                v = item[1].strip()

                if k == 'src':
                    src = v
                elif k == 'dst':
                    dst = v
                elif k == 'env':
                    env = v
                else:
                    print('invalid argv key:%s' %sys.argv[i])
            else:
                print('invalid argv:%s' %sys.argv[i])

        if src and dst and env:
            make(src, dst, env, print)
        else:
            print('momake: missing necessary params(src, dst, env)')
            help()    
    else:
        print('momake: missing necessary params(src, dst, env)')
        help()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        run_gui()
    else:
        run_console()