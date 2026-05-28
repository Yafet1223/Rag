export const formatTime = (iso: string) => {
  const date = new Date(iso);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export const formatDate = (iso: string) => {
  const date = new Date(iso);
  return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
};
