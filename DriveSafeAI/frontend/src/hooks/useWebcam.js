import { useRef, useState, useCallback } from 'react';

export const useWebcam = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const [isWebcamActive, setIsWebcamActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);

  const startWebcam = useCallback(async (deviceId = null) => {
    try {
      setCameraError(null);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }

      const constraints = {
        video: deviceId
          ? { deviceId: { exact: deviceId }, width: { ideal: 640 }, height: { ideal: 480 } }
          : { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setIsWebcamActive(true);
    } catch (err) {
      console.error('Camera access error:', err);
      setCameraError('Unable to access webcam. Please check camera permissions.');
      setIsWebcamActive(false);
    }
  }, []);

  const stopWebcam = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsWebcamActive(false);
  }, []);

  const captureFrameBase64 = useCallback(() => {
    if (!videoRef.current || !isWebcamActive) return null;

    const video = videoRef.current;
    if (!video.videoWidth || !video.videoHeight) return null;

    if (!canvasRef.current) {
      canvasRef.current = document.createElement('canvas');
    }

    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Compress JPEG at 80% quality for fast HTTP payload transmission
    return canvas.toDataURL('image/jpeg', 0.8);
  }, [isWebcamActive]);

  return {
    videoRef,
    isWebcamActive,
    cameraError,
    startWebcam,
    stopWebcam,
    captureFrameBase64,
  };
};
