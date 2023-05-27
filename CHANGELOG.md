# Python-Voice-input

## [1.0.3] - 2023-05-27
### Changed
- TkinterのFrameオブジェクトがある時だけメッセージを出力するように変更  
	これによりライブラリとしての利用を可能にする  
	Changed to output a message only when there is a Tkinter Frame object  
	This makes it possible to use it as a library
- マイクがない時に例外を出すように変更  
	Changed to throw an exception when there is no microphone  

## [1.0.2] - 2022-12-28
### Changed
- 音声認識した文字の表示位置を末尾へ変更  
	Change the display position of voice-recognized characters to the end  