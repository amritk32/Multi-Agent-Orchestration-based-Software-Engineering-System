import AuthForm from './AuthForm';

export default function SignupPage({ onSwitchToLogin }: { onSwitchToLogin: () => void }) {
  return <AuthForm mode="signup" onSwitch={onSwitchToLogin} />;
}
