import React, { useState } from 'react';
import { KeyboardAvoidingView, Platform, StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import { useAuth } from '../context/AuthContext';
import { ErrorBanner, FormInput, PrimaryButton, Screen, TextButton } from '../components/ui';
import { colors } from '../theme/colors';
import type { AuthStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<AuthStackParamList, 'Register'>;

export default function RegisterScreen({ navigation }: Props) {
  const { register } = useAuth();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async () => {
    setError(null);
    if (!username.trim() || !email.trim() || !password) {
      setError('All fields are required.');
      return;
    }
    setLoading(true);
    try {
      await register(username.trim(), email.trim(), password);
    } catch (e: any) {
      setError(e.message ?? 'Registration failed.');
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
          <Text style={styles.title}>Create account</Text>
          <Text style={styles.subtitle}>Start tracking your PST/PFT training</Text>

          <ErrorBanner message={error} />

          <FormInput label="Username" value={username} onChangeText={setUsername} placeholder="jdoe" />
          <FormInput
            label="Email"
            value={email}
            onChangeText={setEmail}
            placeholder="jdoe@example.com"
            keyboardType="email-address"
          />
          <FormInput
            label="Password"
            value={password}
            onChangeText={setPassword}
            placeholder="At least 8 characters"
            secureTextEntry
            onSubmitEditing={onSubmit}
          />

          <View style={styles.spacer} />
          <PrimaryButton title="Create account" onPress={onSubmit} loading={loading} />

          <View style={styles.footer}>
            <Text style={styles.footerText}>Already have an account? </Text>
            <TextButton title="Log in" onPress={() => navigation.navigate('Login')} />
          </View>
        </View>
      </KeyboardAvoidingView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  content: { flex: 1, justifyContent: 'center', paddingHorizontal: 24 },
  title: { fontSize: 30, fontWeight: '800', color: colors.text, marginBottom: 4 },
  subtitle: { fontSize: 15, color: colors.textMuted, marginBottom: 28 },
  spacer: { height: 6 },
  footer: { flexDirection: 'row', justifyContent: 'center', marginTop: 24 },
  footerText: { color: colors.textMuted, fontSize: 14 },
});
