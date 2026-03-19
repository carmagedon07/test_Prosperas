import { useEffect, useRef } from 'react';

export default function usePolling(callback, interval, stopCondition) {
  const savedCallback = useRef();
  const stopRef = useRef(false);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (stopCondition) {
      stopRef.current = true;
      return;
    }
    stopRef.current = false;
    function tick() {
      if (!stopRef.current) savedCallback.current();
    }
    if (!stopCondition) {
      const id = setInterval(tick, interval);
      return () => clearInterval(id);
    }
  }, [interval, stopCondition]);
}
