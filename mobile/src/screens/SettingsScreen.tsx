import React, { useState } from 'react';
import { Alert, StyleSheet, Text, View } from 'react-native';

import { useAuth } from '../context/AuthContext';
import { Card, ErrorBanner, PrimaryButton, Screen, TextButton } from '../components/ui';
import { colors } from '../theme/colors';

export default function SettingsScreen() {
  const { user, logout, deleteAccount } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const onDeleteAccount = () => {
    // In-app account deletion is required by App Store Review Guideline
    // 5.1.1(v) for any app that supports account creation — this can't be
    // a "contact support" flow or a website link.
    Alert.alert(
      'Delete account?',
      'This permanently deletes your account and every entry you\'ve logged. This can\'t be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete my account',
          style: 'destructive',
          onPress: async () => {
            setError(null);
            setDeleting(true);
            try {
              await deleteAccount();
            } catch (e: any) {
              setError(e.message ?? 'Failed to delete account.');
            } finally {
              setDeleting(false);
            }
          },
        },
      ]
    );
  };

  return (
    <Screen>
      <View style={styles.content}>
        <Text style={styles.title}>Settings</Text>

        <ErrorBanner message={error} />

        <Card style={styles.card}>
          <Text style={styles.label}>Signed in as</Text>
          <Text style={styles.value}>{user?.username}</Text>
          <Text style={styles.subvalue}>{user?.email}</Text>
        </Card>

        <View style={styles.spacer} />
        <PrimaryButton title="Log out" onPress={logout} />

        <View style={styles.dangerZone}>
          <Text style={styles.dangerTitle}>Danger zone</Text>
          <TextButton
            title={deleting ? 'Deleting…' : 'Delete account'}
            color={colors.danger}
            onPress={onDeleteAccount}
          />
        </View>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  content: { padding: 20 },
  title: { fontSize: 24, fontWeight: '800', color: colors.text, marginBottom: 18 },
  card: { marginBottom: 24 },
  label: { color: colors.textMuted, fontSize: 12, fontWeight: '600', marginBottom: 4 },
  value: { color: colors.text, fontSize: 18, fontWeight: '700' },
  subvalue: { color: colors.textMuted, fontSize: 13, marginTop: 2 },
  spacer: { height: 8 },
  dangerZone: {
    marginTop: 40,
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    alignItems: 'flex-start',
  },
  dangerTitle: { color: colors.textMuted, fontSize: 12, fontWeight: '700', marginBottom: 10 },
});
