
from voicecontrol import VoiceController


if __name__ == "__main__":
	powerstate = False
	
	vc = VoiceController()

	while True:
		# never stop
		vc.listen()
		
