// Frontend/App/Types/navigationTypes.tsx

import { CompositeScreenProps } from '@react-navigation/native';
import { BottomTabScreenProps } from '@react-navigation/bottom-tabs';
import { StackScreenProps } from '@react-navigation/stack';

export type RootStackParamList = {
    Login: undefined;
    Signup: undefined;
    Recovery: undefined;
    HomeTabs: undefined;
};

export type TabParamList = {
    Perfil: undefined;
    Acuerdos: undefined;
    Ajustes: undefined;
};

export type TabScreenProps<T extends keyof TabParamList> = CompositeScreenProps<
    BottomTabScreenProps<TabParamList, T>,
    StackScreenProps<RootStackParamList>
>;