using System;
using System.Collections.Generic;
using System.Linq;
using INCR;
using MVA;

namespace Main
{
    public static class MainClass
    {
        static void Main(string[] args)
        {
            // new SHET().RunSHET(10);
            //new MVAMain().RunMVA(10);
            new INCRMain().RunINCR(10, 0);
        }
    }
}
