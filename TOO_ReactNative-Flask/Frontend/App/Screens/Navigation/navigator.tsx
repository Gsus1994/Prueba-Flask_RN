// Frontend/App/Screens/Navigation/navigator.tsx

import React from 'react';
import Icon from 'react-native-vector-icons/Ionicons';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { RootStackParamList, TabParamList } from '../../Types/navigationTypes';

// Importar las pantallas
import LoginScreen from '../Auth/login';
import SignupScreen from '../Auth/signup';
import RecoveryScreen from '../Auth/recovery';
import ProfileScreen from '../Pantallas/profile';
import SettingsScreen from '../Pantallas/settings';
import ContractsScreen from '../Pantallas/contracts';

// Crear los navegadores con los tipos
const Tab = createBottomTabNavigator<TabParamList>();
const Stack = createNativeStackNavigator<RootStackParamList>();

// HomeTabs con Acuerdos, Perfil y Ajustes
const HomeTabs = () => (
    <Tab.Navigator
        initialRouteName="Perfil"
        screenOptions={({ route }) => ({
            tabBarIcon: ({ focused, color, size }) => {
                let iconName: string = '';
                if (route.name === 'Acuerdos') {
                    iconName = focused ? 'document' : 'document-outline';
                } else if (route.name === 'Perfil') {
                    iconName = focused ? 'person' : 'person-outline';
                } else if (route.name === 'Ajustes') {
                    iconName = focused ? 'settings' : 'settings-outline';
                }
                return <Icon name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: 'blue',
            tabBarInactiveTintColor: 'gray',
            headerShown: false,
            tabBarStyle: { paddingBottom: 5 },
        })}
    >
        <Tab.Screen name="Acuerdos" component={ContractsScreen} />
        <Tab.Screen name="Perfil" component={ProfileScreen} />
        <Tab.Screen name="Ajustes" component={SettingsScreen} />
    </Tab.Navigator>
);

const AppNavigator = () => (
    <NavigationContainer>
        <Stack.Navigator initialRouteName="Login" screenOptions={{ headerShown: false }}>
            {/* Pantallas de autenticación */}
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Signup" component={SignupScreen} />
            <Stack.Screen name="Recovery" component={RecoveryScreen} />
            {/* Pantallas principales */}
            <Stack.Screen name="HomeTabs" component={HomeTabs} />
        </Stack.Navigator>
    </NavigationContainer>
);

export default AppNavigator;