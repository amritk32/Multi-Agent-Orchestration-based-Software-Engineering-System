import AuthForm from './AuthForm';

export default function LoginPage({ onSwitchToSignup }: { onSwitchToSignup: () => void }) {
  return <AuthForm mode="login" onSwitch={onSwitchToSignup} />;
}
