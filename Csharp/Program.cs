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
            var finalStats = new SHET.SHET().RunSHET(1);
            // new MVAMain().RunMVA(1);
            //new INCRMain().RunINCR(10, 0);
        }
    }
}
