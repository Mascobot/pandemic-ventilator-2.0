import azure.cognitiveservices.speech as speechsdk


speech_key, service_region = "6ac9cad61e8c4622a45699c466b237df", "eastus"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
 


  
audio_filename = "vstart.wav"
audio_output = speechsdk.audio.AudioOutputConfig(filename=audio_filename)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)
text = "Ventilator starting with selected parameters"
result = speech_synthesizer.speak_text_async(text).get()

# Checks result.
if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized to [{}] for text [{}]".format(audio_filename, text))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            print("Error details: {}".format(cancellation_details.error_details))
    print("Did you update the subscription info?")