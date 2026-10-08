import React, { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import * as endpoints from '../api/endpoints';
import { ErrorBanner, FormInput, PrimaryButton, Screen, TextButton } from '../components/ui';
import { colors } from '../theme/colors';
import type { AuthStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<AuthStackParamList, 'ForgotPassword'>;

export default function ForgotPasswordScreen({ navigation }: Props) {
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async () => {
    setError(null);
    setMessage(null);
    if (!email.trim()) {
      setError('Enter your email address.');
      return;
    }
    setLoading(true);
    try {
      const res = await endpoints.forgotPassword(email.trim());
      setMessage(res.message);
    } catch (e: any) {
      setError(e.message ?? 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen>
      <View style={styles.content}>
        <Text style={styles.title}>Reset password</Text>
        <Text style={styles.subtitle}>
          Enter the email on your account and we'll send a reset link.
        </Text>

        <ErrorBanner message={error} />
        {message ? <Text style={styles.message}>{message}</Text> : null}

        <FormInput
          label="Email"
          value={email}
          onChangeText={setEmail}
          placeholder="jdoe@example.com"
          keyboardType="email-address"
        />

        <View style={styles.spacer} />
        <PrimaryButton title="Send reset link" onPress={onSubmit} loading={loading} />

        <View style={styles.footer}>
          <TextButton title="Back to login" onPress={() => navigation.navigate('Login')} />
        </View>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  content: { flex: 1, justifyContent: 'center', paddingHorizontal: 24 },
  title: { fontSize: 28, fontWeight: '800', color: colors.text, marginBottom: 4 },
  subtitle: { fontSize: 14, color: colors.textMuted, marginBottom: 24 },
  message: { color: colors.success, marginBottom: 14, fontSize: 14 },
  spacer: { height: 6 },
  footer: { alignItems: 'center', marginTop: 24 },
});
