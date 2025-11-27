import React from "react";

interface Props {
  message: string;
}

const ErrorBanner: React.FC<Props> = ({ message }) => {
  if (!message) return null;
  return <div className="error-banner">{message}</div>;
};

export default ErrorBanner;
