namespace Helpers
{
    using System;
    using System.Collections.Generic;
    using System.Diagnostics;


    public class Watch : IDisposable
    {
        private readonly Stopwatch sw;
        private List<double> list;

        public Watch(List<double> addToTimes)
        {
            this.sw = new Stopwatch();
            sw.Start();
            if (addToTimes != null)
            {
                this.list = addToTimes;
            }
        }

        public void Dispose()
        {
            sw.Stop();
            if (list != null)
            {
                list.Add(sw.Elapsed.TotalSeconds);
            }
        }
    }
}