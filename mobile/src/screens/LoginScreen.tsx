import React, { useState } from 'react';
import { KeyboardAvoidingView, Platform, StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import { useAuth } from '../context/AuthContext';
import { ErrorBanner, FormInput, PrimaryButton, Screen, TextButton } from '../components/ui';
import { colors } from '../theme/colors';
import type { AuthStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<AuthStackParamList, 'Login'>;

export default function LoginScreen({ navigation }: Props) {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async () => {
    setError(null);
    if (!username.trim() || !password) {
      setError('Enter your username and password.');
      return;
    }
    setLoading(true);
    try {
      await login(username.trim(), password);
    } catch (e: any) {
      setError(e.message ?? 'Login failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen>
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <View style={styles.content}>
          <Text style={styles.title}>Muster</Text>
          <Text style={styles.subtitle}>Log in to your training log</Text>

          <ErrorBanner message={error} />

          <FormInput
            label="Username"
            value={username}
            onChangeText={setUsername}
            placeholder="jdoe"
            returnKeyType="next"
          />
          <FormInput
            label="Password"
            value={password}
            onChangeText={setPassword}
            placeholder="••••••••"
            secureTextEntry
            returnKeyType="go"
            onSubmitEditing={onSubmit}
          />

          <View style={styles.spacer} />
          <PrimaryButton title="Log in" onPress={onSubmit} loading={loading} />

          <View style={styles.row}>
            <TextButton title="Forgot password?" onPress={() => navigation.navigate('ForgotPassword')} />
          </View>
          <View style={styles.footer}>
            <Text style={styles.footerText}>New here? </Text>
            <TextButton title="Create an account" onPress={() => navigation.navigate('Register')} />
          </View>
        </View>
      </KeyboardAvoidingView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  content: { flex: 1, justifyContent: 'center', paddingHorizontal: 24 },
  title: { fontSize: 34, fontWeight: '800', color: colors.text, marginBottom: 4 },
  subtitle: { fontSize: 15, color: colors.textMuted, marginBottom: 28 },
  spacer: { height: 6 },
  row: { marginTop: 16, alignItems: 'center' },
  footer: { flexDirection: 'row', justifyContent: 'center', marginTop: 24 },
  footerText: { color: colors.textMuted, fontSize: 14 },
});
