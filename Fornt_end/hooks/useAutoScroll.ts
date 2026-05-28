"use client";

import { useEffect, useRef } from 'react';

export const useAutoScroll = () => {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.scrollTop = ref.current.scrollHeight;
    }
  });

  return ref;
};
