#include <iostream>
#include <fstream>
#include <cstdlib>
#include <string>
#include <filesystem>
#include <cstring>
#include <set>
#include <thread>
#include <atomic>
#include <conio.h>


using namespace std;
const int MAXAS = 100;

int n, a1, b2, kiekis;
string turingopav, turingopav2, pavadinimas;
string busen[MAXAS], nauja_busen[MAXAS];
char simb1[MAXAS], simb2[MAXAS],
     naujas_simb1[MAXAS], naujas_simb2[MAXAS],
     kryptis1[MAXAS], kryptis2[MAXAS];
set<char> simbolis_set;

void patikrinimas() {
    if (_kbhit()) {
        char komanda = _getch();
        if (komanda == 'q' || komanda == 'Q') {
            cout << "Iseinama is programos" << endl;
            exit(0);
        } else if (komanda == 's' || komanda == 'S') {
            cout << "Programa sustabdyta. Paspausk R pratesti arba Q - baigti darba" << endl;
            while (true) {
                char komanda2 = _getch();
                if (komanda2 == 'r' || komanda2 == 'R') {
                    cout << "Tesiama programa" << endl;
                    break;
                } else if (komanda2 == 'q' || komanda2 == 'Q') {
                    cout << "Iseinama is programos" << endl;
                    exit(0);
                }
            }
        } else if (komanda == 'r' || komanda == 'R') {
            cout << "Tesiamas darbas" << endl;
        }
    }
}

void nuskaitymas(const string& pavadinimas) {
    ifstream fr(pavadinimas);
    if (!fr) {
        cerr << "Netinkamas failo pavadinimas!" << endl;
        exit(1);
    }
    fr >> n;
    if (n == 2) {
        fr >> turingopav >> turingopav2;
        fr >> a1 >> b2;
    } else {
        fr >> turingopav;
        fr >> a1;
    }
    kiekis = 0;
    if (n == 2) {
        while (fr >> busen[kiekis] >> simb1[kiekis] >> simb2[kiekis] >> naujas_simb1[kiekis] >> naujas_simb2[kiekis] >> kryptis1[kiekis] >> kryptis2[kiekis] >> nauja_busen[kiekis]) {
            kiekis++;
        }
        cout << "Pradiniai kodai:" << endl;
        cout << "[" << turingopav << "]" << endl;
        cout << "[" << turingopav2 << "]" << endl;
        cout << "----------------------------------------------------------------" << endl;
    } else {
        while (fr >> busen[kiekis] >> simb1[kiekis] >> naujas_simb1[kiekis] >> kryptis1[kiekis] >> nauja_busen[kiekis]) {
            kiekis++;
        }
        cout << "Pradinis kodas:" << endl;
        cout << "[" << turingopav << "]" << endl;
        cout << "----------------------------------------------------------------" << endl;
    }
    fr.close();
}

void masina() {
    int ilgis = turingopav.length(), k = 0;
    int ilgis2 = turingopav2.length();
    string pirmbusena = "0", ats;
    int infinite = 0, suma = 0, h = 0;
    string temp = "Neaptiktas";
    bool HALT = false;
    string zodis;
    int galas = 0;
    if (n == 1) {
        while (a1 >= 0 && a1 < ilgis) {
            HALT = false;
            for (int m = 0; m < kiekis; m++) {
                if (a1 == ilgis) {
                    a1 = ilgis - 1;
                    galas++;
                }
                if (simb1[m] == turingopav[a1] && busen[m] == pirmbusena) {
                    if (galas == 1) {
                        a1 = ilgis;
                        galas = 0;
                    }
                    turingopav[a1] = naujas_simb1[m];
                    pirmbusena = nauja_busen[m];
                    if (pirmbusena == "H" || pirmbusena == "X" || pirmbusena == "done") {
                        cout << "\nTuringo masina sekmingai baige" << endl;
                        return;
                    }
                    cout << turingopav;
                    cout << " || Busena: " << pirmbusena << "; ";
                    cout << "Simbolis: "<<naujas_simb1[m];
                    cout << " ; operaciju skaicius: " << suma << endl;
                    if (kryptis1[m] == 'R') {
                        a1++;
                        if (a1 >= turingopav.size()) {
                            turingopav.resize(turingopav.size() + 1);
                            turingopav.insert(a1, "_");
                        }
                    } else if (kryptis1[m] == 'L') {
                        if (a1 == 0) {
                            turingopav.insert(0, "_");
                        } else {
                            a1--;
                        }
                    }
                    if (a1 < 0 || a1 >= ilgis) {
                        break;
                    }
                    for (int x = 0; x < a1; x++) {
                        cout << " ";
                    }
                    cout << "Y" << endl;
                    infinite++;
                    suma++;
                    patikrinimas();
                    if (infinite%3000==0) {
                        cout << "Ar tai programos pabaiga?" << endl;
                        cout << "Taip/Ne ";
                        cin >> ats;


                        if (ats == "Taip" || ats == "taip" || ats == "yes" || ats == "Yes" || ats == "TAIP" || ats == "YES") {
                            return;
                        } if (ats == "Ne" || ats == "ne" || ats == "no" || ats == "No" || ats == "NE" || ats == "NO"||ats == "nE"||ats == "nO") {
                            infinite = 0;

                        }
                    }
                    HALT = true;
                    break;
                }
            }
            if (!HALT) {
                cout << "Nera tokios busenos: " << pirmbusena << "; su simboliu: " << turingopav[a1] << endl;
                break;
            }
            if (zodis == "stop" || zodis == "Stop" || zodis == "STOP") {
                break;
            }
        }
    }
    if (n >= 2) {
        int galas2 = 0;
        while (a1 >= 0 && a1 <= ilgis && b2 >= 0 && b2 <= ilgis2) {
            HALT = false;
            for (int m = 0; m < kiekis; m++) {
                if (a1 == ilgis) {
                    a1 = ilgis - 1;
                    galas++;
                }
                if (b2 == ilgis2) {
                    b2 = ilgis2 - 1;
                    galas2++;
                }
                if (simb1[m] == turingopav[a1] && simb2[m] == turingopav2[b2] && busen[m] == pirmbusena) {
                    if (galas == 1) {
                        a1 = ilgis;
                        galas = 0;
                    }
                    if (galas2 == 1) {
                        b2 = ilgis2;
                        galas2 = 0;
                    }
                    turingopav[a1] = naujas_simb1[m];
                    turingopav2[b2] = naujas_simb2[m];
                    pirmbusena = nauja_busen[m];
                    if (pirmbusena == "H" || pirmbusena == "X" || pirmbusena == "done") {
                        cout << "\nTuringo masina sekmingai baige" << endl;
                        return;
                    }
                    cout << turingopav;
                    cout << " || Busena: " << pirmbusena << "; ";
                    cout << "Simbolis: " << simb1[m];
                    cout << " ; operaciju skaicius: " << suma << endl;
                    if (kryptis1[m] == 'R')
                        a1++;
                    else if (kryptis1[m] == 'L')
                        a1--;
                    for (int x = 0; x < a1; x++) {
                        cout << " ";
                    }
                    cout << "Y" << endl;
                    cout << turingopav2;
                    cout << " || Busena: " << pirmbusena << "; ";
                    cout << "Simbolis: " << simb2[m];
                    cout << " ; operaciju skaicius: " << suma << endl;
                    if (kryptis2[m] == 'R')
                        b2++;
                    else if (kryptis2[m] == 'L')
                        b2--;
                    for (int x = 0; x < b2; x++) {
                        cout << " ";
                    }
                    cout << "Y" << endl;
                    infinite++;
                    suma++;
                    patikrinimas();
                    cout << "----------------------------------------------------------------" << endl;
                    if (infinite%3000==0) {
                            cout << "Ar tai programos pabaiga?" << endl;
                            cout << "Taip/Ne ";
                            cin >> ats;


                            if (ats == "Taip" || ats == "taip" || ats == "yes" || ats == "Yes" || ats == "TAIP" || ats == "YES") {
                                return;
                            } if (ats == "Ne" || ats == "ne" || ats == "no" || ats == "No" || ats == "NE" || ats == "NO"||ats == "nE"||ats == "nO") {
                                infinite = 0;

                            }
                        }
                    HALT = true;
                    break;
                }
            }
            if (!HALT) {
                cout << "Nera tokios busenos: " << pirmbusena << "; su simboliais: "
                     << turingopav[a1] << " ir " << turingopav2[b2] << endl;
                break;
            }
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Klaida" << endl;
        return 1;
    }
    string fpavadinimas = argv[1];
    cout << "Failas " << fpavadinimas << endl;
    nuskaitymas(fpavadinimas);
    masina();
    return 0;
}
