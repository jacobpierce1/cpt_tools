#include <iostream>
#include <fstream>
#include <string>
#include<iomanip>

using namespace std;


double omega(double mass, int q ){
	double el = 548.579909;
	double m_cs = 132905451.961;
	double wc_cs = 657844.45;
	
	double wc;
	wc = q*wc_cs*(m_cs - el)/ (mass);
	
	return wc;
	}
	
double hydro_mass(int a, int b, int c, int d,int e, int f, int g, int q, double m_rad){
	double el = 548.579909;
	double m_c = 12000000.0;
	double m_h = 1007825.03223;
	double m_o = 15994914.6196;
	double m_n = 14003074.0043;
	double m_cl35 = 34968852.68;
	double m_cl37 = 36965902.60;
	
	double mass;
	mass = m_c*a + m_h*b + m_o*c + m_n*d + m_rad*e +m_cl35*f + m_cl37*g - q*el;
	
	return mass;
	}
	
int main(){
	double el = 548.579909;
	string name[1100];
	string name1[1100];
	int A[1100];
	double branch[1100];
	double mass[1100];
	double mass_err[1100];
	int A1[1100];
	double branch1[1100];
	double mass1[1100];
	double mass_err1[1100];
	
	int x = 0;

	ifstream textfile;
	textfile.open("cf252_and_stable_masses.txt");
	while(x<1046){
		textfile >> A[x];
		textfile >> name[x];
		textfile >> branch[x];
		textfile >> mass[x];
		textfile >> mass_err[x];
		//cout << A[x] << '\t' << name[x] << '\t' << branch[x] <<'\t' << mass[x]<< endl;
		x++;
	}
	textfile.close();
	
	double wc[1100];

	int a,b,c,d,e,f,g,i,qs;
	int q = 2.0; // set the charge state
	int MASS = 153.0; // and the mass number
	double mass_new;
	ofstream output;
	output.open("mass153_2+_molecules_2018.txt"); // and the name of the output file...
	
	output<< "A"<<'\t'<<"el"<<'\t'<<"branch"<<'\t'<<"#"<<'\t'<<"C"<<'\t'<<"H"<<'\t'<<"O"<<'\t'<<"N"<<'\t'<<"Cl35"<<'\t'<<"Cl37"<<'\t'<< "mass"<<'\t'<<"w_c";
	for(i=0;i<1046; i++){// radio
		for(a =0; a<11; a++){// C
			for(b=0;b<22; b++){// H
				for(c=0;c<5; c++){// O
					for(d=0;d<5; d++){// N
						for(e=1;e<2; e++){// # of radios
							for(f=0; f<5; f++){
								for(g=0; g<5; g++){									
									if (branch[i] > 0.0001){
										if(A[i]*e + a*12.0 + b*1.0 + c*16.0 + d*14.0 + f*35.0 + g*37.0 == MASS){
											mass_new = hydro_mass(a,b,c,d,e,f,g,q,mass[i]);
											output<<'\n'<<A[i]<<'\t'<<name[i]<<'\t'<<branch[i]<<'\t'<<e<<'\t'<<a<<'\t'<<b<<'\t'<<c<<'\t'<<d<<'\t'<<f<<'\t'<<g<<'\t'<<setprecision(11)<< mass_new + q*el <<'\t'<<omega(mass_new, q);
										}									
									}
								}
							}
						}
					}
				}
			}
		}
	}
	output.close();
getchar();
return 0;
}
