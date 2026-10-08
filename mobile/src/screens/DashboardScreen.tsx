import React, { useCallback, useState } from 'react';
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import * as endpoints from '../api/endpoints';
import type { DashboardResponse } from '../api/types';
import { Card, ErrorBanner, PrimaryButton, Screen, TextButton } from '../components/ui';
import { ProgressBar } from '../components/ProgressBar';
import { colors, tierColor, tierLabel } from '../theme/colors';
import { useAuth } from '../context/AuthContext';
import type { AppStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<AppStackParamList, 'Dashboard'>;

export default function DashboardScreen({ navigation }: Props) {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (isRefresh = false) => {
    isRefresh ? setRefreshing(true) : setLoading(true);
    setError(null);
    try {
      const res = await endpoints.fetchDashboard();
      setData(res);
    } catch (e: any) {
      setError(e.message ?? 'Failed to load dashboard.');
    } finally {
      isRefresh ? setRefreshing(false) : setLoading(false);
    }
  }, []);

  // Reload every time the screen regains focus (e.g. after logging a new entry).
  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  return (
    <Screen>
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => load(true)} tintColor={colors.text} />}
      >
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Welcome back{user ? `, ${user.username}` : ''}</Text>
            <Text style={styles.subtitle}>
              {data ? `${data.total_entries} entries logged` : ' '}
            </Text>
          </View>
          <TextButton title="Settings" onPress={() => navigation.navigate('Settings')} />
        </View>

        <ErrorBanner message={error} />

        {loading && !data ? (
          <ActivityIndicator color={colors.primary} style={styles.loader} />
        ) : (
          data?.cards.map((card) => (
            <Card key={card.key} style={styles.cardSpacing}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardLabel}>{card.label}</Text>
                <Text style={[styles.tierBadge, { color: tierColor(card.tier) }]}>
                  {tierLabel(card.tier)}
                </Text>
              </View>

              {card.entry ? (
                <>
                  <Text style={styles.cardValue}>
                    {card.entry.display_value}
                    {card.unit === 'reps' ? ' reps' : ''}
                  </Text>
                  <ProgressBar ratio={card.ratio ?? 0} color={tierColor(card.tier)} />
                  <View style={styles.scaleRow}>
                    <Text style={styles.scaleText}>{card.min_display}</Text>
                    <Text style={styles.scaleText}>{card.competitive_display}</Text>
                    <Text style={styles.scaleText}>{card.max_display}</Text>
                  </View>
                  <Text style={styles.dateText}>
                    Logged {card.entry.entry_date}
                    {card.entry.notes ? ` · ${card.entry.notes}` : ''}
                  </Text>
                </>
              ) : (
                <Text style={styles.emptyText}>No entries yet — log your first one.</Text>
              )}
            </Card>
          ))
        )}

        <View style={styles.actions}>
          <PrimaryButton title="Log a result" onPress={() => navigation.navigate('LogEntry')} />
          <View style={styles.actionSpacer} />
          <TextButton title="View full history" onPress={() => navigation.navigate('History')} />
        </View>
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  content: { padding: 20, paddingBottom: 40 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 20,
  },
  greeting: { fontSize: 22, fontWeight: '800', color: colors.text },
  subtitle: { fontSize: 13, color: colors.textMuted, marginTop: 2 },
  loader: { marginTop: 40 },
  cardSpacing: { marginBottom: 14 },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  cardLabel: { fontSize: 15, fontWeight: '700', color: colors.text },
  tierBadge: { fontSize: 12, fontWeight: '700' },
  cardValue: { fontSize: 28, fontWeight: '800', color: colors.text, marginBottom: 10 },
  scaleRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 6 },
  scaleText: { fontSize: 11, color: colors.textMuted },
  dateText: { fontSize: 12, color: colors.textMuted, marginTop: 10 },
  emptyText: { fontSize: 14, color: colors.textMuted },
  actions: { marginTop: 12 },
  actionSpacer: { height: 14 },
});
