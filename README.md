# Python-Voice-input


## 概要 Description
音声入力ツール

音声入力をします。認識した音声を文字で表示します。あわせてファイルに出力します。  

## 特徴 Features

- Google Speech Recognition を使用して音声認識します。  
- 認識した音声を文字で画面表示(認識順)します。  
- 認識した音声を文字でファイル出力(話した順)します。  
- 音声認識に関する設定(音声と雑音のしきい値、しきい値の動的調整のオン/オフ)ができます。  
- 画面表示するフォントのサイズを変更できます。  
- Sphinx を使用した音声認識のソースを提供します。   

## 依存関係 Requirement

- Python 3.8.5  
- SpeechRecognition 3.8.1  
- PyAudio 0.2.11+ (マイク入力のために必要)  
- pocketsphinx 5.0.0  

## 使い方 Usage

- 操作  
	- 音声入力の開始  
		「開始」ボタンをクリック    
	- 音声入力の終了  
		「ストップ」と話す(単語として認識するように)  
		「ストップ」を認識しても音声入力待ちになることがあります  
		その場合はもう一度何か話してください  
		※Sphinx版は「おわり」で判断します
	- ファイル出力
		ファイル出力は自動で行います  
		exeファイルのあるフォルダの「音声入力.txt」に追記します
		ファイルがなければ作ります
		音声入力ごとに「◆年月日 時分秒」が区切りとして挿入されます
	-設定
		次の項目が設定できます    
		- しきい値：音声と雑音のしきい値を指定します(0〜3500)  
			雑音が大きい環境ほど大きくします  
		- フォントサイズ：表示する文字のサイズを指定します  
		- 動的しきい値調整：チェックを付けるとしきい値の調整を動的に行います  
			静かな環境の場合、効果的ではありませんでした  

- 画面の説明  
	- 音声入力待ちの時に「n?」と表示します(表示されるのを待つ必要はありません)  
	- 入力した音声の認識を開始すると「n?」と表示します  
	- 認識が完了すると「n===>認識した文字」と表示します  
	- 上記のnは1からの整数で入力の順番です  
	- 認識できなかった場合、「？」と表示します(ほとんどは無音(雑音)です)  
	- 「ストップ」が認識できると「「ストップ」を認識したので終了します」と表示します  
		続けて入力した文字を表示します。この内容をファイル出力します  

- しきい値について
	- 音声入力中に「？」がたくさん出る場合はしきい値を大きくしてください。
	- 開始ボタンを押しても「n?」が表示されない時はしきい値を小さくしてください。

## 制限事項  

- マイクが既定のデバイスとして認識されている必要があります
- インターネットに接続している泌悠があります
- Google Speech Recognition について Google に情報が見つかりませんが動作しています。  
	Google Speech Recognition がサービスされなくなると動作しなくなります。  
- マイクに風があたる様な環境では会話の切れ目がうまく認識できないことが多くなります
- 動的しきい値調整を有効にした場合に、しきい値が20以下に設定された場合に20に戻します  
	しきい値が小さすぎると少しの音で解析してしまうためです  
- Sphinx版は音響モデルのフォルダと言語モデルと辞書のファイル名をソースで指定する必要があります


## 依存関係パッケージのインストール方法 Installation

- pip install pyaudio  
- pip install SpeechRecognition
- pip install pocketsphinx

## プログラムの説明サイト Program description site

- [音声入力で文章作成するアプリの作り方【Python】 - プログラムでおかえしできるかな](https://juu7g.hatenablog.com/entry/Python/speech-recognition/voice-input-GSR)  
- [CMU Sphinx音響モデルの適応【Python】 - プログラムでおかえしできるかな](https://juu7g.hatenablog.com/entry/Python/speech-recognition/voice-input-sphinx)  
- [◆voice_input_GSR モジュールについて](https://juu7g.hatenablog.com/entry/Python/rpa/pywinauto/voice-browser#voice_input_GSR-モジュールについて)

## 作者 Authors
juu7g

## ライセンス License
このソフトウェアは、MITライセンスのもとで公開されています。LICENSEファイルを確認してください。  
This software is released under the MIT License, see LICENSE file.

