# Text_Annotation
[![](https://img.shields.io/badge/Python-3.5,3.6-blue.svg)](https://www.python.org/)
[![](https://img.shields.io/badge/numpy-1.14.3-brightgreen.svg)](https://pypi.python.org/pypi/numpy/1.14.3)
[![](https://img.shields.io/badge/keras-2.1.6-brightgreen.svg)](https://pypi.python.org/pypi/keras/2.1.6)
[![](https://img.shields.io/badge/tensorflow-1.4,1.6-brightgreen.svg)](https://pypi.python.org/pypi/tensorflow/1.6.0)<br>

文本标注

## **项目介绍**
上次研究了一下文本生成，刚好工作上有实体识别的业务需求，就研究了一下文本标注。<br>
特征抽取部分的代码和文本生成没太大区别，LSTM改成了双向，最后一层的逐帧Softmax改成CRF而已。<br>
参考了几篇博文的分析：《CRF序列标注模型几个问题的理解》、《使用RNN解决NLP中序列标注问题的通用优化思路》，在此表示感谢！

## **模块简介**
### 模块结构
结构很简单，方法在Text_Annotation文件夹内，还有三个简单的demo，分别是分词、词性标注和关系抽取。Text_Annotation文件夹包括：<br>
<br>
**数据**：data文件夹中<br>
小黄鸡聊天记录(导入数据load_chat.py，我上传了部分，完整版来源<https://github.com/fateleak/dgk_lost_conv>，在此表示感谢！)<br>
若干篇法律法规word文档(导入数据load_docx.py)<br>
创建实体关系(假设只有相邻的名词和动词存在关系，creat_relation.py)<br>
<br>
**预处理**：Data_process.py是个方法，用于载入数据、分词、编码、填充<br>
<br>
**网络**：net文件夹<br>
双向LSTM+CRF，model_crf.py<br>
双向LSTM+Softmax，model_Softmax.py<br>
关系分类器SVM/Logostic/Dense，model_relation.py<br>
<br>
**训练**：train文件夹<br>
实体识别，train_annotation.py<br>
关系抽取，train_relation.py<br>
<br>
**标注**：annotate文件夹<br>
location.py，实体定位、筛选、配对<br>
annotate.py，句向量、实体识别<br>
<br>
**范例**：demo文件夹<br>
annotate_cut.py，用于分词<br>
annotate_pos.py，词性标注<br>
demo_creat_relation.py创建实体对关系数据<br>
demo_creat_relation_mp.py多进程创建实体对关系数据(进程多了会报sess不能创建的错误)<br>
data文件夹，存放自己生成的用于训练关系抽取的数据<br>
<br>
![](https://github.com/renjunxiang/Text_Annotation/blob/master/picture/theory.jpg)
<br>

### 一些说明
1.不同于LSTM文本生成，CRF要求数据reshape回[batchsize, max_seq_len, num_tags]，所以生成的时候务必保证网络的shape和输入文本的shape一致。<br>
<br>
2.分词的话相对标注简单一些，只要BMES基本就够了，实体识别的话标注会复杂一些，每个实体类别的都有BME，例如名词N的标注为NB/NM/NE/NS。测试集如果和训练集存在较大的差异，包括专业领域、句法结构等，训练次数越多效果会越差，可以理解为过拟合严重；反之，则训练的越充分，效果越好，可以理解为完全学会了训练集的标注方法。由于没有标签数据，我用jieba对小黄鸡语料库先分词，转成BMES标签后训练，对于法律领域的分词效果惨不忍睹。用jieba对法律文档做了词性标注，训练名词(n)和动词(v)，网上找了一段法律陈述，效果一般。<br>
<br>
3.编码过程使用了keras的Tokenizer，他的num_words是包含0的，也就是保留春词语数量实际是num_words-1。不同于分类和生成，标注要注意数据不能在Tokenizer的时候删掉低频词。所以我并没有使用texts_to_sequences，而是手动把排名超过num_words和不在语料库的字编码转为num_words。<br>
<br>
~~4.有时间我会尝试一下逐帧Softmax的效果，理论上每个词的输出是结合了上下文语义，而且从唐诗生成的效果看是完全可以学到上下文的。~~<br>
抽空完成了用逐帧Softmax做标注，分词倾向于单个字，词性标注会出现嵌套的情况，效果的确要比CRF差一些。<br>
<br>
5.一个句子可能对应多个关系，实体配对也依赖一些外部的规则，好像没办法在一个网络同时实现实体识别和关系抽取。分开做的话，关系抽取就必须先用实体识别的网络计算词向量，效率会很低。<br>
<br>
6.创建实体对标注数据以及批量处理的时候，由于标注函数最初只为了演示，会反复的载入sess参数并且只处理一条文本，所以速度有点慢。本来想用多进程的(demo_creat_relation_mp.py)，但是会报Failed to create session这个错误，不知道什么原因。实际应用中预测多条的时候，可能要进一步优化。另外keras和tensorflow同时使用，必须先运行一下keras的模型，否则keras无法创建计算图。<br>

## 结果展示
**先要train.py进行训练，这时会保存网络参数和预处理参数，annotate.py会导入这些参数用于预测(分词)，参考demo.py**<br>
<br>
### CRF的效果
1.**语料库中闲聊语句的词汇和句法基本都出现了，效果还可以。**<br><br>
![](https://github.com/renjunxiang/Text_Annotation/blob/master/picture/chat.jpg)<br><br>
2.**语料库中字基本都出现了，但词汇频率很低，句法结构也相差较大，效果一般。**<br><br>
![](https://github.com/renjunxiang/Text_Annotation/blob/master/picture/ai.jpg)<br><br>
3.**语料库中字很多没出现，句法结构基本不同，效果很差，训练次数越多越不准确，会倾向于按照语料库的句法结构去分。**<br><br>
![](https://github.com/renjunxiang/Text_Annotation/blob/master/picture/law.jpg)<br><br>
4.**针对名词、动词的标注，效果还可以。**<br><br>
![](https://github.com/renjunxiang/Text_Annotation/blob/master/picture/pos.jpg)<br><br>
5.**最终版本：实体识别+关系抽取**<br><br>
![](https://github.com/renjunxiang/Text_Annotation/blob/master/picture/relation.jpg)<br><br>

### Softmax的效果
1.**分词倾向于逐个字切分，勉强能看。**<br><br>
![](https://github.com/renjunxiang/Text_Annotation/blob/master/picture/ai_softmax.jpg)<br><br>
2.**针对名词、动词的标注，效果低于CRF，勉强能看。**<br><br>
![](https://github.com/renjunxiang/Text_Annotation/blob/master/picture/pos_softmax.jpg)<br><br>

