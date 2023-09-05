#include <iostream>
#include <time.h>
#include <iomanip>
#include <vector>
#include <fstream>
using namespace std;

const int MISSILE = 0;
const int FIREBALL = 1;
const int DAGGER = 2;
const int STAFF = 3;
const int GLOBE = 4;
const int STONESKIN = 5;
const int STRENGTH = 6;
const int HEAL = 7;


// Display info
void printInfo(vector<vector<float>>& weights, vector<bool>& state);

// Q-Learning or SARSA steps with function approximation
int selectAction(int numActions, vector<float> Q_state, bool dontHaveHeal, float epsilon);
void performSelectedAction(int action);
float obtainReward(int oppDamageTaken, int meDamageTaken, int& HP, int action, bool donthaveHeal);
void updateWeights(vector<vector<float>>& weights, vector<float> Q_state, vector<float> Q_state_p, vector<bool> state_p, 
	vector<bool> state, int action, float reward, float lr);
void updateState(vector<bool>& state, vector<bool> state_p);

// Helper Functions
void cinInfos(int& oppAction, int& oppDamageTaken, int& meDamageTaken, int& oppBelow50, int& oppBelow10, int& iHaveGlobe,
	int& iHaveStoneskin, int& iHaveStrength, int& oppHasGlobe, int& oppHasStoneskin, int& oppHasStrength, int& endSignal);
vector<float> calculateTable(vector<vector<float>> weights, vector<bool> state, int numActions, int numFeatures);


int main()
{
	srand(time(NULL));

	int numRounds;
	cin >> numRounds;

	int roundCounter = 0;

	const int numActions = 8;
	const int numFeatures = 11;
	// [opponent below 50%, opponent below 10%, I'm below 50%, I'm below 10%, opponent has Globe, opponent has Stoneskin, 
	// opponent has Strength, I have Globe, I have Stoneskin, I have Strength, I don't have Heal anymore]

	// the weights table used for function approximation
	vector<vector<float>> weights(numActions, vector<float>(numFeatures + 1, 0.0));
	weights[7][11] = -30;

	// Reading initial weights from initWeights.txt if it exists. Otherwise start with all weights equal to 0.0
	ifstream file;
	file.open("initWeights.txt");
	if (file) {
		for (int i = 0; i < numActions * (1 + numFeatures); i++) {
			file >> weights[i / (numFeatures + 1)][i % (numFeatures + 1)];
		}
	}

	file.close();

	vector<bool> state(numFeatures, false);    // the current state represented as vector of binary feature
	vector<bool> state_p = state;  // the next state State Prime

	int oppAction; int oppDamageTaken; int meDamageTaken; int oppBelow50; int oppBelow10; int iHaveGlobe;
	int iHaveStoneskin; int iHaveStrength; int oppHasGlobe; int oppHasStoneskin; int oppHasStrength; int endSignal;

	// Reinforcement Learning
	int roundCount = 1;
	for (int i = 0; i < numRounds; i++) {
		int HP = 100;
		state = { false, false, false, false, false, false, false, false, false, false, false };
		state_p = state;

		if (roundCount == 25) {
			// Write the final weights to initWeights.txt
			ofstream file1;
			file1.open("initWeights.txt", ofstream::out | ofstream::trunc);
			for (int i = 0; i < numActions * (1 + numFeatures); i++) {
				file1 << weights[i / (numFeatures + 1)][i % (numFeatures + 1)] << " ";
			}

			file1.close();
		}

		float lr = 0.15;  // learning rate
		float epsilon = 0.1;	// epsilon

		while (true) {
			// Q[State, Action_i]
			vector<float> Q_state = calculateTable(weights, state, numActions, numFeatures);

			int action = selectAction(numActions, Q_state, state[10], epsilon);
			if (action == 7) { state_p[10] = true; }

			performSelectedAction(action);

			cinInfos(oppAction, oppDamageTaken, meDamageTaken, oppBelow50, oppBelow10, iHaveGlobe, iHaveStoneskin,
				iHaveStrength, oppHasGlobe, oppHasStoneskin, oppHasStrength, endSignal);

			state_p = { oppBelow50 == 1, oppBelow10 == 1, HP - meDamageTaken < 50, HP - meDamageTaken < 10, oppHasGlobe == 1,
			oppHasStoneskin == 1, oppHasStrength == 1, iHaveGlobe == 1, iHaveStoneskin == 1, iHaveStrength == 1, state_p[10] };

			float reward = obtainReward(oppDamageTaken, meDamageTaken, HP, action, state[10]);

			// Q[State_p, Action_i]
			vector<float> Q_state_p = calculateTable(weights, state_p, numActions, numFeatures);

			updateWeights(weights, Q_state, Q_state_p, state_p, state, action, reward, lr);

			updateState(state, state_p);

			printInfo(weights, state);

			if (endSignal != 0) { break; }
		}
		roundCount++;
	}

	printInfo(weights, state);
	cerr << endl;
	cout.flush();
	system("pause");
	return 0;

}


// prints the weights and the features in the current state
void printInfo(vector<vector<float>>& weights, vector<bool>& state)
{
	int numActions = weights.size();
	int numColumns = weights[0].size();

	cerr << endl << "Weights: " << endl;
	for (int i = 0; i < numActions; i++) {
		cerr << "Action" << i << " ";
		for (int j = 0; j < numColumns; j++) {
			cerr << setw(8) << left;
			cerr << setprecision(3) << weights[i][j];
		}
		cerr << endl;
	}

	cerr << "The current state: " << endl;
	cerr << "      Always1   ";
	for (unsigned int i = 0; i < state.size(); i++) {
		cerr << setw(8) << left;
		cerr << state[i];
	}
	cerr << endl << endl;
}

int selectAction(int numActions, vector<float> Q_state, bool dontHaveHeal, float epsilon) {
	int action = 0;

	if (rand() % 100 < epsilon * 100.0) {
		do {
			action = rand() % numActions;
		} while (action == 7 && dontHaveHeal);
		return action;
	}

	float max_Q = -100.0;
	for (int i = 0; i < numActions; i++)
		if (Q_state[i] > max_Q) {
			max_Q = Q_state[i];
			action = i;
		}

	return action;
}

void performSelectedAction(int action) { cout << action << endl; }

float obtainReward(int oppDamageTaken, int meDamageTaken, int& HP, int action, bool dontHaveHeal) {
	int oldHP = HP;
	HP -= meDamageTaken;

	if (HP > 100) { HP = 100; }
	else if (HP < 0) { HP = 0; }

	if (action == 7) {
		if (dontHaveHeal) {
			return -50 - (oldHP - HP);
		}
		if (oldHP > 50) { return (HP - oldHP) - 50; }

		return 70;
	}

	return 1.0f * oppDamageTaken - (oldHP - HP);
}

void updateWeights(vector<vector<float>>& weights, vector<float> Q_state, vector<float> Q_state_p, vector<bool> state_p, 
	vector<bool> state, int action, float reward, float lr) {
	float max_Q_p = -100.0f;
	for (int i = 0; i < Q_state_p.size(); i++)
		if (Q_state_p[i] >= max_Q_p) {
			max_Q_p = Q_state_p[i];
		}

	weights[action][0] += lr * (reward + 0.15f * max_Q_p - Q_state[action]);

	for (int i = 1; i < state_p.size() + 1; i++)
		if (state[i - 1]) {
			weights[action][i] += lr * (reward + 0.15f * max_Q_p - Q_state[action]);
		}
}

void updateState(vector<bool>& state, vector<bool> state_p) { state = state_p; }

void cinInfos(int& oppAction, int& oppDamageTaken, int& meDamageTaken, int& oppBelow50, int& oppBelow10, int& iHaveGlobe,
	int& iHaveStoneskin, int& iHaveStrength, int& oppHasGlobe, int& oppHasStoneskin, int& oppHasStrength, int& endSignal) {
	cin >> oppAction;
	cin >> oppDamageTaken;
	cin >> meDamageTaken;
	cin >> oppBelow50;
	cin >> oppBelow10;
	cin >> iHaveGlobe;
	cin >> iHaveStoneskin;
	cin >> iHaveStrength;
	cin >> oppHasGlobe;
	cin >> oppHasStoneskin;
	cin >> oppHasStrength;
	cin >> endSignal;
}

vector<float> calculateTable(vector<vector<float>> weights, vector<bool> state, int numActions, int numFeatures) {
	vector<float> Q_state;
	for (int i = 0; i < numActions; i++) {
		float Q = weights[i][0];
		for (int j = 0; j < numFeatures; j++)
			if (state[j])
				Q += weights[i][j + 1];
		Q_state.push_back(Q);
	}

	return Q_state;
}

